#ifndef OMEGALIB_HPP
#define OMEGALIB_HPP

#include <algorithm>
using std::find;
using std::sort;

#include <iostream>
#include <fstream>
#include <locale>
#include <map>
#include <sstream>
#include <string>

#include <util/Lists.hpp>
#include <util/Strings.hpp>
#include <util/OS.hpp>
using util::OS;

#include <basic/Dynamic_Array.h>
#include <basic/Iterator.h>

#include <omega/parser/AST.hh>
#include <omega/hull.h>
#include <omega/closure.h>
#include <omega/reach.h>
#include <codegen.h>
#include <omega/parser/parser.tab.hh>

using namespace omega;

#define ASN_OP ":="
#define PROMPT ">>>"

#define IN(cont,item) (find((cont).begin(),(cont).end(),(item))!=(cont).end())
#define LEN(cont) ((unsigned)(cont).size())

int omega_run(std::istream *is, std::ostream *os);

namespace omglib {
struct UninterpFunc {
    string name;
    vector<string> args;
    unsigned arity;
    unsigned order;
    string oldName;
    vector<string> oldArgs;
    int oldArity;

    explicit UninterpFunc(const string& name = "", unsigned arity = 1, unsigned order = 0) {
        this->name = name;
        this->arity = arity;
        this->order = order;
        this->oldName = "";
        this->oldArity = 0;
    }

    UninterpFunc(const UninterpFunc& other) {
        this->name = other.name;
        this->args = other.args;
        this->arity = other.arity;
        this->order = other.order;
        this->oldName = other.oldName;
        this->oldArgs = other.oldArgs;
        this->oldArity = other.oldArity;
    }

    unsigned num_args() const {
        return this->args.size();
    }

    void add_arg(const string& arg) {
        this->args.push_back(arg);
    }

    string to_string() const {
        ostringstream oss;
        oss << this->name << "(" << this->arity << ") -> (";
        int count = 0;
        int last = this->args.size() - 1;
        for (const string& arg : this->args) {
            oss << arg;
            if (count < last) {
                oss << ",";
            }
            count += 1;
        }
        oss << ")";
        return oss.str();
    }
};

//struct OmegaLib : public PolyLib {
struct OmegaLib {
protected:
    vector<string> _kwords = {"exists", "union", "intersection", "complement", "compose", "inverse",
                              "domain", "range", "hull", "codegen", "farkas", "forall", "given", "and",
                              "or", "not", "within", "subsetof", "supersetof", "symbolic"};

    vector<string> _iterators;
    map<string, UninterpFunc> _ufuncs;

    bool isknown(const string& cond, const vector<string>& iters, const vector<string>& exists) const {
        // TODO: Simplify this logic!!!
        bool known = false;
        vector<char> rel_ops = {'>', '<', '='};
        vector<char> arith_ops = {'+', '-', '*', '/'};
        for (const string& operand : Strings::split(cond, rel_ops)) {
            known = !IN(iters, operand) && !IN(exists, operand);
            if (!known) {
                break;
            }
        }

        if (known) {
            for (const string& kword : _kwords) {
                known = !Strings::in(cond, kword);
                if (!known) {
                    break;
                }
            }
        }

        if (known) {
            for (const string& operand : Strings::split(cond, arith_ops)) {
                known = !IN(iters, operand) && !IN(exists, operand);
                if (!known) {
                    break;
                }
            }
        }

        return known;
    }

    string getiter(const string& arg, const vector<string>& iters) const {
        string iter;
        for (const char ch : arg) {
            iter += ch;
            if (IN(iters, iter)) {
                break;
            }
        }
        return iter;
    }

    string preprocess(const string& relation, string& relid) {
        size_t pos = relation.find(ASN_OP);
        string relstr = relation;
        if (pos != string::npos) {
            relid = Strings::rtrim(relation.substr(0, pos - 1));
            relstr = Strings::ltrim(relation.substr(pos + 2));
        }
        return Strings::removeWhitespace(relstr);
    }

    void parse_relation(const string& relation, vector<string>& iters,
                        string& condstr, vector<string>& conds) {
        size_t pos = relation.find(':');
        if (pos != string::npos) {
            string iterstr = relation.substr(2, pos - 3);
            iters = Strings::split(iterstr, ',');
            condstr = Strings::rtrim(relation.substr(pos + 1), '}');
            conds = Strings::split(condstr, "&&");
        }
    }

    void parse_conds(const string& relation, const vector<string>& conds, const vector<string>& iters,
                     vector<string>& exists, vector<string>& knowns, map<string, size_t>& symcons,
                     map<string, UninterpFunc>& ufuncs) {
        // Collect conditions and uninterpreted functions...
        for (const string& cond : conds) {
            size_t pos = cond.find("exists(");
            if (pos != string::npos) {
                vector<string> evars = Strings::split(cond.substr(pos + 7, cond.find(':', pos + 7)), ',');
                for (const string& evar : evars) {
                    exists.push_back(evar);
                }
            }

            vector<string> items = Strings::words(cond);
            for (const string& item : items) {
                string lcitem = Strings::lower(item);
                if (!IN(iters, item) && !IN(_kwords, lcitem)) {
                    if (Strings::in(relation, item + '(') && ufuncs.find(item) == ufuncs.end()) {
                        UninterpFunc ufunc(item, 1, ufuncs.size());
                        ufuncs[item] = ufunc;
                    }
                    if (symcons.find(item) == symcons.end() && ufuncs.find(item) == ufuncs.end() &&
                        find(exists.begin(), exists.end(), item) == exists.end()) {
                        symcons[item] = symcons.size();
                    }
                }
            }
            if (isknown(cond, iters, exists)) {
                knowns.push_back(cond);
            }
        }
    }

    string parse_knowns(string& relation, vector<string>& iters, vector<string>& conds, string& condstr,
                        vector<string>& knowns, map<string, size_t>& symcons, string& symlist) {
        // Separate set string for codegen argument from those for given clause.
        string given;
        if (LEN(knowns) > 0) {
            for (const string& known : knowns) {
                conds.erase(find(conds.begin(), conds.end(), known));
            }
            relation = Strings::replace(relation, condstr, Strings::join(conds, "&&"));
            given = Strings::join(knowns, "&&");
        }

        if (!symcons.empty()) {
            vector<string> symkeys = Lists::keys<string, size_t>(symcons);
            for (const string& symkey : symkeys) {
                if (symlist.empty()) {
                    symlist = symkey;
                } else if (symlist.find(symkey) == string::npos) {
                    symlist += "," + symkey;
                }
            }
        }

        // Assume symbolic constants (non-functions) are positive
        if (given.empty() && symlist.find("N") != string::npos) {
            given += "N>3";
            if (symlist.find("C") != string::npos) {
                given += "&&C>3";
            }
        }

        return given;
    }

    map<string, UninterpFunc> parse_ufuncs(const string& relation, const vector<string>& iters,
                                           const map<string, UninterpFunc>& ufuncs) {
        map<string, UninterpFunc> newfuncs;
        // U-funcs are tricky, need to consider the args...
        // 1st Pass: Collect all data on u-funcs.
        for (auto ufpair : ufuncs) {
            string ufname = ufpair.first;
            UninterpFunc ufunc = ufpair.second;

            vector<string> arglists;
            size_t fpos = relation.find(ufname);
            while (fpos >= 0 && fpos != string::npos) {
                fpos += LEN(ufname);
                size_t lpos = relation.find('(', fpos);
                size_t rpos = relation.find(')', lpos + 1);
                string sub = relation.substr(lpos + 1, rpos - lpos - 1);
                if (!IN(arglists, sub)) {
                    arglists.push_back(sub);
                }
                fpos = relation.find(ufname, rpos + 1);
            }

            std::sort(arglists.begin(), arglists.end());
            for (const string& arglist : arglists) {
                vector<string> args = Strings::split(arglist, ',');
                ufunc.arity = LEN(args);
                for (unsigned i = 0; i < ufunc.arity; i++) {
                    string arg = args[i];
                    if (ufunc.num_args() <= i) {  // New arg!
                        // Check whether arg is an iterator
                        if (!IN(iters, arg)) {
                            ufunc.oldArgs.push_back(arg);
                            arg = getiter(arg, iters);
                        }
                        ufunc.add_arg(arg);
                    } else if (arg != ufunc.args[i]) {
                        UninterpFunc newfunc = UninterpFunc(ufunc);
                        newfunc.oldName = ufunc.name;
                        if (Strings::isDigit(newfunc.name[newfunc.name.size() - 1])) {
                            newfunc.name += "_";
                        }
                        newfunc.name += to_string(i + 1);
                        newfunc.oldArgs.push_back(arg);
                        newfuncs[newfunc.name] = newfunc;
                    }
                }
            }
            newfuncs[ufname] = ufunc;
        }

        return newfuncs;
    }

    map<string, UninterpFunc> update_ufuncs(const string& relation, const vector<string>& iters, string& symlist,
                                            const map<string, UninterpFunc>& ufuncs) {
        map<string, UninterpFunc> newfuncs;

        // 2nd Pass: To prevent prefix errors, need to ensure leading arg includes preceding iterators...
        for (auto ufpair : ufuncs) {
            UninterpFunc ufunc = ufpair.second;
            if (ufunc.arity > 0) {
                ufunc.oldArity = ufunc.arity;
                vector<string> newargs;
                for (const string& arg : ufunc.args) {
                    int ipos = Lists::index<string>(iters, arg);
                    if (ipos >= 0) {
                        newargs = Lists::slice<string>(iters, 0, ipos - 1);
                        break;
                    }
                }
                if (ufunc.oldArgs.empty()) {
                    ufunc.oldArgs = ufunc.args;
                }
                if (!newargs.empty()) {
                    ufunc.arity += newargs.size();
                    ufunc.args.insert(ufunc.args.begin(), newargs.begin(), newargs.end());
                }
            }
            string ufstr = ufunc.name + '(' + to_string(ufunc.arity) + ')';
            if (symlist.empty()) {
                symlist = ufstr;
            } else if (symlist.find(ufstr) == string::npos) {
                symlist += "," + ufstr;
            }
            newfuncs[ufpair.first] = ufunc;
        }

        return newfuncs;
    }

    void update_relations(const map<string, UninterpFunc>& ufuncs, string& relation, string& given) {
        //  3rd Pass: Replace the occurrences of the UFs in the original relation...
        for (auto ufpair : ufuncs) {
            string ufname = ufpair.first;
            UninterpFunc ufunc = ufpair.second;
            string oldcall;
            if (!ufunc.oldName.empty()) {
                oldcall = ufunc.oldName + '(' + Strings::join(ufunc.oldArgs, ",") + ')';
            } else if (ufunc.arity > ufunc.oldArity) {
                oldcall = ufname + '(' + Strings::join(ufunc.oldArgs, ",") + ')';
            }
            if (!oldcall.empty()) {
                string newcall = ufname + '(' + Strings::join(ufunc.args, ",") + ')';
                if (oldcall != newcall) {
                    relation = Strings::replace(relation, oldcall, newcall);
                    given = Strings::replace(given, oldcall, newcall);
                }
            }
        }
    }

    string codegen_expr(const string& relname, const vector<string>& schedules) {
        string cgexpr;
        if (!schedules.empty()) {
            cgexpr = " ";
            unsigned n = 0, nschedules = schedules.size();
            for (const auto& sched : schedules) {
                string schedname = sched.substr(0, sched.find(' '));
                cgexpr += schedname + ":" + relname;
                if (n < nschedules - 1) {
                    cgexpr += ',';
                }
                n += 1;
            }
        } else {
            cgexpr = '(' + relname + ')';
        }
        return cgexpr;
    }

    void merge_ufuncs(const map<string, UninterpFunc>& srcmap, map<string, UninterpFunc>& destmap) {
        for (const auto& iter : srcmap) {
            destmap[iter.first] = iter.second;
        }
    }

public:
    vector<string> in_iterators() const {
        return _iterators;
    }

    vector<string> out_iterators() const {
        vector<string> outiters;
        for (unsigned i = 0; i < _iterators.size(); i++) {
            outiters.emplace_back("t" + to_string(i + 1));
        }
        return outiters;
    }

    string codegen(const vector<string>& names, map<string, string>& relmap,
                   map<string, vector<string> >& schedmap) {
        //string iterlist;
        string symlist;
        string givens;
        string cgexpr;

        map<string, string> newmap;
        vector<string> allschedules;
        vector<string> maxiters;

        unsigned nstatements = 1;
        for (const string& name : names) {
            string relname = name;
            string relation = relmap[relname];
            vector<string> schedules = schedmap[relname];
            nstatements = schedules.size();

            string relstr;
            string condstr;
            map<string, size_t> symcons;
            map<string, UninterpFunc> ufuncs;

            vector<string> iters;
            vector<string> conds;
            vector<string> exists;
            vector<string> knowns;

            string result = preprocess(relation, relname);
            parse_relation(result, iters, condstr, conds);
            parse_conds(result, conds, iters, exists, knowns, symcons, ufuncs);
            string given = parse_knowns(result, iters, conds, condstr, knowns, symcons, symlist);

            ufuncs = parse_ufuncs(result, iters, ufuncs);
            ufuncs = update_ufuncs(result, iters, symlist, ufuncs);
            update_relations(ufuncs, result, given);

            if (!given.empty() && givens.find(given) == string::npos) {
                if (!givens.empty()) {
                    givens += "&&";
                }
                givens += given;
            }

            //if (!iters.empty()) {
//                for (const string& iter : iters) {
//                    if (iterlist.empty()) {
//                        iterlist = iter;
//                    } else if (iterlist.find(iter) == string::npos) {
//                        iterlist += "," + iter;
//                    }
//                }

            if (iters.size() > maxiters.size()) {
                maxiters = iters;
            }
            for (const string& sched : schedules) {
                allschedules.push_back(sched);
            }

            cgexpr += codegen_expr(relname, schedules) + ',';
            if (iters.size() > _iterators.size()) {
                _iterators = iters;
            }
            //}

            merge_ufuncs(ufuncs, _ufuncs);
            newmap[relname] = result;
        }

        ostringstream oss;
        if (!symlist.empty()) {
            oss << "symbolic " << symlist << ";\n";
        }
        //if (!iterlist.empty()) {
        if (!maxiters.empty()) {
            for (const string& name : names) {
                oss << name << " := " << newmap[name] << ";\n";
            }
            for (const auto& sched : allschedules) {
                oss << sched << ";\n";
            }
            cgexpr = cgexpr.substr(0, cgexpr.size() - 1);
            oss << "codegen" << cgexpr;
            if (!givens.empty()) {
                oss << " given " << "{" << Strings::str<string>(maxiters) << ": " << givens << "}";
            }
            oss << ";\n";
        }

        cerr << oss.str();
        return parse(oss.str(), nstatements);
    }

    /// TODO: This is the legacy version of 'codegen', verify unit tests and then remove it!
    string codegen(const string& relation, const string& id = "I", const vector<string>& schedules = {}) {
        map<string, size_t> symcons;
        map<string, UninterpFunc> ufuncs;

        vector<string> iters;
        vector<string> conds;
        vector<string> exists;
        vector<string> knowns;

        string relId, relStr;
        string condStr;
        string iterStr;
        string symList;

        size_t pos = relation.find(ASN_OP);
        if (pos != string::npos) {
            relId = Strings::rtrim(relation.substr(0, pos - 1));
            relStr = Strings::ltrim(relation.substr(pos + 2));
        } else {
            relId = id;
            relStr = relation;
        }

        string result = Strings::removeWhitespace(relStr);

        pos = result.find(':');
        if (pos != string::npos) {
            iterStr = result.substr(2, pos - 3);
            iters = Strings::split(iterStr, ',');

            condStr = Strings::rtrim(result.substr(pos + 1), '}');
            conds = Strings::split(condStr, "&&");
        }

        // Collect conditions and uninterpreted functions...
        for (const string& cond : conds) {
            pos = cond.find("exists(");
            if (pos != string::npos) {
                vector<string> evars = Strings::split(cond.substr(pos + 7, cond.find(':', pos + 7)), ',');
                for (const string& evar : evars) {
                    exists.push_back(evar);
                }
            }

            vector<string> items = Strings::words(cond);
            for (const string& item : items) {
                string lcitem = Strings::lower(item);
                if (!IN(iters, item) && !IN(_kwords, lcitem)) {
                    if (Strings::in(result, item + '(') && ufuncs.find(item) == ufuncs.end()) {
                        UninterpFunc ufunc(item, 1, ufuncs.size());
                        ufuncs[item] = ufunc;
                    }
                    if (symcons.find(item) == symcons.end() && ufuncs.find(item) == ufuncs.end() &&
                        find(exists.begin(), exists.end(), item) == exists.end()) {
                        symcons[item] = symcons.size();
                    }
                }
            }
            if (isknown(cond, iters, exists)) {
                knowns.push_back(cond);
            }
        }

        // Separate set string for codegen argument from those for given clause.
        string given;
        if (LEN(knowns) > 0) {
            for (const string& known : knowns) {
                conds.erase(find(conds.begin(), conds.end(), known));
            }
            result = Strings::replace(result, condStr, Strings::join(conds, "&&"));
            given = "{[" + Strings::join(iters, ",") + "]: " + Strings::join(knowns, "&&") + "}";
        }

        if (!symcons.empty()) {
            vector<string> symkeys = Lists::keys<string, size_t>(symcons);
            symList = Strings::join(symkeys, ",") + ",";
        }

        // U-funcs are tricky, need to consider the args...
        // 1st Pass: Collect all data on u-funcs.
        map<string, UninterpFunc> newfuncs;
        for (auto ufpair : ufuncs) {
            string ufname = ufpair.first;
            UninterpFunc ufunc = ufpair.second;

            vector<string> arglists;
            size_t fpos = result.find(ufname);
            while (fpos >= 0 && fpos != string::npos) {
                fpos += LEN(ufname);
                size_t lpos = result.find('(', fpos);
                size_t rpos = result.find(')', lpos + 1);
                string sub = result.substr(lpos + 1, rpos - lpos - 1);
                if (!IN(arglists, sub)) {
                    arglists.push_back(sub);
                }
                fpos = result.find(ufname, rpos + 1);
            }

            std::sort(arglists.begin(), arglists.end());
            for (const string& arglist : arglists) {
                vector<string> args = Strings::split(arglist, ',');
                ufunc.arity = LEN(args);
                for (unsigned i = 0; i < ufunc.arity; i++) {
                    string arg = args[i];
                    if (ufunc.num_args() <= i) {  // New arg!
                        // Check whether arg is an iterator
                        if (!IN(iters, arg)) {
                            ufunc.oldArgs.push_back(arg);
                            arg = getiter(arg, iters);
                        }
                        ufunc.add_arg(arg);
                    } else if (arg != ufunc.args[i]) {
                        UninterpFunc newfunc = UninterpFunc(ufunc);
                        newfunc.oldName = ufunc.name;
                        if (Strings::isDigit(newfunc.name[newfunc.name.size() - 1])) {
                            newfunc.name += "_";
                        }
                        newfunc.name += to_string(i + 1);
                        newfunc.oldArgs.push_back(arg);
                        newfuncs[newfunc.name] = newfunc;
                    }
                }
            }
            newfuncs[ufname] = ufunc;
        }

        ufuncs = newfuncs;
        newfuncs.clear();

        // 2nd Pass: To prevent prefix errors, need to ensure leading arg includes preceding iterators...
        for (auto ufpair : ufuncs) {
            UninterpFunc ufunc = ufpair.second;
            if (ufunc.arity > 0) {
                ufunc.oldArity = ufunc.arity;
                vector<string> newargs;
                for (const string& arg : ufunc.args) {
                    if (IN(iters, arg)) {
                        newargs = Lists::slice<string>(iters, 0, Lists::index<string>(iters, arg) - 1);
                        break;
                    }
                }
                ufunc.arity += LEN(newargs);
                if (LEN(ufunc.oldArgs) < 1) {
                    ufunc.oldArgs = ufunc.args;
                }
                for (const string& arg : newargs) {
                    ufunc.args.insert(ufunc.args.end() - 1, arg);
                }
            }
            symList += ufunc.name + '(' + to_string(ufunc.arity) + "),";
            newfuncs[ufpair.first] = ufunc;
        }

        ufuncs = newfuncs;

        //  3rd Pass: Replace the occurrences of the UFs in the original relation...
        for (auto ufpair : ufuncs) {
            string ufname = ufpair.first;
            UninterpFunc ufunc = ufpair.second;
            string oldcall;
            if (!ufunc.oldName.empty()) {
                oldcall = ufunc.oldName + '(' + Strings::join(ufunc.oldArgs, ",") + ')';
            } else if (ufunc.arity > ufunc.oldArity) {
                oldcall = ufname + '(' + Strings::join(ufunc.oldArgs, ",") + ')';
            }
            if (!oldcall.empty()) {
                string newcall = ufname + '(' + Strings::join(ufunc.args, ",") + ')';
                if (oldcall != newcall) {
                    result = Strings::replace(result, oldcall, newcall);
                    given = Strings::replace(given, oldcall, newcall);
                }
            }
        }

        ostringstream oss;
        if (!symList.empty()) {
            symList = symList.substr(0, symList.size() - 1);
            oss << "symbolic " << symList << ";\n";
        }
        if (!iterStr.empty()) {
            oss << relId << " := " << result << ";\n";

            string cgexpr;
            if (!schedules.empty()) {
                cgexpr = " ";
                unsigned n = 0, nschedules = schedules.size();
                for (const auto& sched : schedules) {
                    oss << sched << ";\n";
                    string schedId = sched.substr(0, sched.find(' '));
                    cgexpr += schedId + ":" + relId;
                    if (n < nschedules - 1) {
                        cgexpr += ',';
                    }
                    n += 1;
                }
            } else {
                cgexpr = '(' + relId + ')';
            }
            oss << "codegen" << cgexpr;
            if (!given.empty()) {
                oss << " given " << given;
            }
            oss << ";\n";
        }

        _ufuncs = ufuncs;
        cerr << oss.str();

        return parse(oss.str());
    }

    string parse(const string& code, unsigned nstatements = 1) {
        vector<string> lines;
        if (!code.empty()) {
            istringstream iss(code);
            ostringstream oss;
            omega_run(&iss, &oss);
            //oss << "for (t1 = 0; t1 < N; t1++) {\nprintf(\"Omega+ dies in pain!\\n\");\n}\n";
            lines = Strings::filter(Strings::split(oss.str(), '\n'), PROMPT, true);
        } else {
            for (unsigned i = 0; i < nstatements; i++) {
                lines.emplace_back("s" + to_string(i) + "();");
            }
            lines.emplace_back("");
        }
        return Strings::join(lines, "\n");
    }

    void omega_cmd(const string& code, ostream& os) {
        string exec = "/usr/local/bin/omegacalc";
        string file = "/tmp/omega.in";

        ofstream ofs(file.c_str());
        ofs << code << endl;
        ofs.close();

        string cmd = exec + " " + file;
        string res = OS::run(cmd);
        os << res;
    }

    map<string, string> macros() {
        map<string, string> macros;
        for (auto itr = _ufuncs.begin(); itr != _ufuncs.end(); ++itr) {
            UninterpFunc ufunc = itr->second;
            string ufName = ufunc.name;
            string arrName = ufName;
            if (!ufunc.oldName.empty())
                arrName = ufunc.oldName;
            string lhs = ufName + "(" + Strings::join(ufunc.args, ",") + ")";
            string rhs = arrName + "[(" + Strings::join(ufunc.oldArgs, "),(") + ")]";
            macros[lhs] = rhs;
        }
        return macros;
    }
};
}

#endif  // OMEGALIB_HPP
