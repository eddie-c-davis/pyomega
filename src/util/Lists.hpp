#ifndef POLYEXT_LISTS_HP
#define POLYEXT_LISTS_HP

#include <algorithm>
using std::sort;
using std::copy;
#include <initializer_list>
#include <map>
#include <vector>
using std::initializer_list;
using std::string;
using std::map;
using std::vector;
#include <sstream>
using std::ostringstream;
#include "Strings.hpp"

class Lists {
public:
    template <typename T>
    static inline vector<T> initListToVec(const initializer_list<T> list) {
        vector<T> vec;
        for (const auto& elem : list) {
            vec.push_back(elem);
        }
        return vec;
    }

    template <typename K, typename V>
    static inline vector<K> keys(const map<K,V>& inmap) {
        vector<K> keys;
        keys.reserve(inmap.size());
        for(auto const& pair: inmap) {
            keys.push_back(pair.first);
        }
        std::sort(keys.begin(), keys.end());
        return keys;
    }

    template <typename K, typename V>
    static inline vector<K> values(const map<K,V>& inmap) {
        vector<V> vals;
        vals.reserve(inmap.size());
        for(auto const& pair: inmap) {
            vals.push_back(pair.second);
        }
        sort(vals.begin(), vals.end());
        return vals;
    }

    template <typename T>
    static inline int index(const vector<T>& in, T item, int start = 0) {
        ptrdiff_t pos = distance(in.begin() + start, find(in.begin() + start, in.end(), item));
        if (pos >= in.size()) {
            return -1;
        } else {
            return (int) pos;
        }
    }

    template <typename T>
    static inline vector<T> slice(const vector<T>& in, int start, int stop = -1) {
        vector<T> out;
        if (stop >= 0) {
            out.reserve(stop - start);
            for (int i = start; i <= stop; i++) {
                out.push_back(in[i]);
            }
        }
        return out;
    }

    template <typename T>
    static inline bool equal(const vector<T>& lhs, const vector<T>& rhs, unsigned size) {
        bool equal = true;
        for (unsigned i = 0; i < size && i < lhs.size() && i < rhs.size() && equal; i++) {
            equal &= (lhs[i] == rhs[i]);
        }
        return equal;
    }

    template <typename T>
    static inline vector<T> append(const vector<T>& lhs, const vector<T>& rhs) {
        vector<T> res = lhs;
        for (const auto& elem : rhs) {
            res.push_back(elem);
        }
        return res;
    }

    template <typename T>
    static inline vector<T> match(const vector<T>& vec, T item) {
        vector<T> matches;
        ostringstream os;
        os << item;
        string mstr = os.str();

        for (const T& elem : vec) {
            os.str("");
            os << elem;
            string estr = os.str();

            if (Strings::in(estr, mstr)) {
                matches.push_back(elem);
            }
        }
        return matches;
    }

    template <typename T>
    static inline bool match(const vector<T>& lhs, const vector<T>& rhs, unsigned size = string::npos) {
        bool result = true;
        for (unsigned i = 0; i < size && i < lhs.size() && i < rhs.size() && result; i++) {
            ostringstream lstr;
            lstr << lhs[i];
            ostringstream rstr;
            rstr << rhs[i];
            result &= (lstr.str() == rstr.str());
        }
        return result;
    }

    template <typename T>
    static inline void read(vector<T>& elems, const string& file, const char delim = ',') {
        if (!file.empty()) {
            char ch = ' ';
            string token;
            FILE* fp = fopen(file.c_str(), "r");

            unsigned pos = 0;
            while (ch != EOF) {
                ch = (char) fgetc(fp);
                if (ch == delim) {
                    if (!token.empty()) {
                        elems[pos++] = Strings::convert<T>(token);
                        token = "";
                    }
                } else {
                    token += ch;
                }
            }

            if (!token.empty()) {
                elems[pos++] = Strings::convert<T>(token);
            }

            fclose(fp);
        }
    }

    static inline void write(vector<int>& elems, const string& file, const char delim = ',') {
        write<int>(elems, file, delim, "%d");
    }

    static inline void write(vector<unsigned>& elems, const string& file, const char delim = ',') {
        write<unsigned>(elems, file, delim, "%u");
    }

    static inline void write(vector<float>& elems, const string& file, const char delim = ',') {
        write<float>(elems, file, delim, "%g");
    }

    static inline void write(vector<double>& elems, const string& file, const char delim = ',') {
        write<double>(elems, file, delim, "%lg");
    }

    template <typename T>
    static inline void write(const vector<T>& elems, const string& file = "", const char delim = ',', const string pattern = "%s") {
        FILE* fp = stderr;
        if (!file.empty()) {
            fp = fopen(file.c_str(), "w");
        }
        unsigned endpos = elems.size() - 1;
        for (unsigned i = 0; i <= endpos; i++) {
            fprintf(fp, pattern.c_str(), elems[i]);
            if (i < endpos) {
                fprintf(fp, "%c", delim);
            }
        }
        if (!file.empty()) {
            fclose(fp);
        }
    }
};

#endif // POLYEXT_LISTS_HP
