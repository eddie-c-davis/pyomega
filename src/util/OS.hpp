#ifndef _OS_HPP_
#define _OS_HPP_

#include <cstdio>
#include <cstdlib>
#include <unistd.h>
#include <string>
using std::string;

#define BUFFSIZE 1024

namespace util {
class OS {
public:
static string run(const string& cmd) {
	char buffer[BUFFSIZE];
	string result = "";

	FILE* pipe = popen(cmd.c_str(), "r");
	if (pipe) {
		while (!feof(pipe)) {
			if (fgets(buffer, BUFFSIZE, pipe) != NULL) {
				result += string(buffer);
            }
		}
		pclose(pipe);
	} else {
	    fprintf(stderr, "ERROR: Cannot run command: %s\n", strerror(errno));
	}

	return result;
}

static int ncpus() {
    int ncpus = 1;
#ifdef _SC_NPROCESSORS_ONLN
    ncpus = sysconf(_SC_NPROCESSORS_ONLN);
#endif
    return ncpus;
}

static string username() {
    return getenv("USER");
}

static string hostname() {
    return getenv("HOST");
}

static string timestamp() {
    char buffer[BUFFSIZE];
    time_t rawtime;
    struct tm *ti;

    time(&rawtime);
    ti = localtime(&rawtime);

    sprintf(buffer, "%02d/%02d/%04d %02d:%02d:%02d", ti->tm_mon + 1, ti->tm_mday,
            ti->tm_year + 1900, ti->tm_hour, ti->tm_min, ti->tm_sec);

    return string(buffer);
}
};
}

#endif

