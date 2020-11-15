#ifndef STRINGS_HPP
#define STRINGS_HPP

#include <algorithm>
#include <cstring>
#include <string>
#include <sstream>
#include <vector>
using namespace std;

#ifdef LLVM_ENABLE
#include "llvm/Pass.h"
#include "llvm/IR/Module.h"
using namespace llvm;
#endif

class Strings {
public:
#ifdef LLVM_ENABLE
	static inline string str(const Instruction* instr) {
        string str;
        raw_string_ostream rso(str);
        instr->print(rso);
        return str;
	}

    static inline string str(const Type* type) {
        string str;
        raw_string_ostream rso(str);
        type->print(rso);
        return str;
    }

    static inline string str(const Value* value) {
        string str;
        raw_string_ostream rso(str);
        value->print(rso);
        return str;
    }
#endif

    static inline bool in(const string& input, const string& sub, bool words = false) {
        size_t pos = 0;
	    if (words) {
            string token;
            for (char chr : input) {
                if ((chr >= 'A' && chr <= 'Z') || (chr >= 'a' && chr <= 'z') ||
                    (chr >= '0' && chr <= '9') || chr == '_') {
                    token += chr;
                } else {
                    if (token == sub) {
                        return pos;
                    }
                    token = "";
                }
                pos += 1;
            }
            if (token == sub) {
                return pos;
            }
            if (pos == input.size()) {
                pos = string::npos;
            }
        } else {
            pos = input.find(sub);
        }
        return pos != string::npos;
    }

    static vector<std::string> split(const string& str, char delim = ' ') {
        vector<string> tokens;
        string token;
        istringstream stream(str);
        while (getline(stream, token, delim)) {
            tokens.push_back(token);
        }
        return tokens;
    }

    static vector<std::string> split(const string& str, const string& delim) {
        vector<string> tokens;
        char* cstr = (char*) str.c_str();
        char* cdelim = (char*) delim.c_str();
        char* token = strtok(cstr, cdelim);

        while (token != NULL) {
            tokens.push_back(string(token));
            token = strtok(NULL, cdelim);
        }
        return tokens;
    }

    static vector<std::string> split(const string& str, const vector<char>& delims) {
        string token;
	    vector<string> tokens;
        for (char ch : str) {
            if (find(delims.begin(), delims.end(), ch) == delims.end()) {
                token += ch;
            } else if (token.size() > 0) {
                tokens.push_back(token);
                token = "";
            }
        }
        if (token.size() > 0) {
            tokens.push_back(token);
        }
        return tokens;
    }

    template<typename T=string>
    static string join(const vector<T>& items, const string& delim = "\n") {
        ostringstream oss;
        if (!items.empty()) {
            size_t last = items.size() - 1;;
            for (size_t i = 0; i < last; i++) {
                oss << items[i] << delim;
            }
            oss << items[last];
        }
        return oss.str();
	}

    static vector<std::string> filter(const vector<string>& items, const string& pattern, bool negate = false) {
	    vector<string> matches;
	    if (!pattern.empty()) {
            for (string item : items) {
                bool match = in(item, pattern);
                if (negate) {
                    match = !match;
                }
                if (match) {
                    matches.push_back(item);
                }
            }
        }
	    return matches;
	}

    // trim from start
    static inline string ltrim(const string& str) {
        string copy = str;
        copy.erase(copy.begin(), find_if(copy.begin(), copy.end(), [](int ch) {
            return !isspace(ch);
        }));
        return copy;
    }

    // trim from start
    static inline string ltrim(const string& str, char tchar) {
	    return ltrim(str, {tchar});
    }

    static inline string ltrim(const string& str, initializer_list<char> tchars) {
        size_t pos = 0;
        string trimmed;
        for (char tchar : tchars) {
            for (; pos < str.size() && str[pos] == tchar; pos += 1);
            if (pos < str.size()) {
                trimmed = str.substr(pos);
            } else {
                trimmed = str;
            }
        }
        return trimmed;
    }

    // trim from end
    static inline string rtrim(const string &str) {
        string copy = str;
        copy.erase(find_if(copy.rbegin(), copy.rend(), [](int ch) {
            return !isspace(ch);
        }).base(), copy.end());
        return copy;
    }

    // trim from end
    static inline string rtrim(const string &str, char tchar) {
        return rtrim(str, {tchar});
    }

    static inline string rtrim(const string &str, initializer_list<char> tchars) {
        size_t pos = str.size() - 1;
        string trimmed;
	    for (char tchar : tchars) {
            for (; pos > 0 && str[pos] == tchar; pos -= 1);
            if (pos > 0) {
                trimmed = str.substr(0, pos + 1);
            } else {
                trimmed = str;
            }
        }
        return trimmed;
    }

    // trim from both ends
    static inline string trim(const string &str) {
        string trimStr = ltrim(str);
        trimStr = rtrim(trimStr);
        return trimStr;
    }

    // trim from both ends
    static inline string trim(const string &str, char tchar) {
        string trimStr = ltrim(str, tchar);
        trimStr = rtrim(trimStr, tchar);
        return trimStr;
    }

    static inline string trim(const string &str, initializer_list<char> tchars) {
        string trimStr = ltrim(str, tchars);
        trimStr = rtrim(trimStr, tchars);
        return trimStr;
    }

    static inline string removeWhitespace(const string& in) {
	    string out;
	    for (char ch : in) {
	        if (!isspace(ch)) {
	            out += ch;
	        }
	    }
        return out;
	}

    static inline bool isDigit(const string& str) {
        return str == digits(str);
    }

	static inline bool isDigit(const char ch) {
	    return (ch >= '0' && ch <= '9');
	}

    static inline bool isNumber(const string& str) {
	    for (const char chr : str) {
	        if (!isDigit(chr) && chr != 'e' && chr != 'E' && chr != '-' && chr != '+' && chr != '.') {
	            return false;
	        }
	    }
        return true;
    }

    static inline bool isOperator(const char ch) {
	    return (ch >= '"' && ch <= '0') || (ch >= '<' && ch <= '@') || (ch == '^');
	}

	static inline vector<string> words(const string& in) {
        string word;
	    vector<string> words;
	    bool inword = false;
	    for (char ch : in) {
	        if ((ch >= 'A' && ch <= 'Z') || (ch >= 'a' && ch <= 'z') || ch == '_') {
                inword = true;
                word += ch;
            } else if (inword && (ch >= '0' && ch <= '9')) {
                word += ch;
	        } else if (!word.empty()) {
	            words.push_back(word);
	            word = "";
                inword = false;
	        }
	    }
        if (word.size() > 0) {
            words.push_back(word);
        }
        return words;
	}

    static inline string lower(const string& str) {
        string lower;
        for (int ch : str) {
            lower += (char) tolower(ch);
        }
        return lower;
    }

    static inline string upper(const string& str) {
        string upper;
        for (int ch : str) {
            upper += (char) toupper(ch);
        }
        return upper;
    }

    static inline string replace(const string& input, const string& from, const string& to, bool words = false) {
        string output;
	    if (!from.empty()) {
            size_t pos = 0;
            if (words) {
                string token;
                for (char chr : input) {
                    if ((chr >= 'A' && chr <= 'Z') || (chr >= 'a' && chr <= 'z') ||
                        (chr >= '0' && chr <= '9') || chr == '_') {
                        token += chr;
                    } else {
                        if (token == from) {
                            token = to;
                        }
                        output += token + chr;
                        token = "";
                    }
                }
                if (token == from) {
                    token = to;
                }
                output += token;
            } else {
                output = input;
                while ((pos = output.find(from, pos)) != string::npos) {
                    output.replace(pos, from.length(), to);
                    pos += to.length(); // In case 'to' contains 'from', like replacing 'x' with 'yx'
                }
            }
        }
        return output;
    }

    static inline string digits(const string& input) {
        string dig = "";
        for (char chr : input) {
            if (chr >= '0' && chr <= '9') {
                dig += chr;
            }
        }
        return dig;
    }

    static inline string number(const string& input) {
        string num;
        for (unsigned i = 0; i < input.size(); i++) {
            string sub = input.substr(i, 1);
            if (isNumber(sub)) {
                num += sub;
            }
        }
        return num;
    }

    static inline string fixParens(const string& input) {
        string fixed = "";
        char prev = 0;
        for (char curr : input) {
            if (!((curr == '(' || curr == ')') && curr == prev)) {
                fixed += curr;
            }
            prev = curr;
        }
        return fixed;
	}

    template<typename T>
    static inline string str(const vector<T> &vec) {
	    ostringstream os;
        os << '[';
        unsigned last = vec.size() - 1;
        for (unsigned i = 0; i <= last; i++) {
            os << vec[i];
            if (i < last) {
                os << ',';
            }
        }
        os << ']';
        return os.str();
    }

    template <typename T>
    static inline T convert(const string& in) {
	    T out;
        istringstream is(in);
        is >> out;
        return out;
	}

    template <typename T>
	static inline vector<string> convert(const vector<T>& vec) {
	    ostringstream os;
	    vector<string> strings;
	    for (const T& elem : vec) {
	        os.str("");
	        os << elem;
	        strings.push_back(os.str());
	    }
	    return strings;
	}
};

#endif /* STRINGS_HPP */
