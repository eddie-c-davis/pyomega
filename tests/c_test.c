// C program of nested function
// with the help of gcc extension
#include <stdio.h>

int view();

int main() {
    auto int view();
    int local_var = 1;
    view(); // calling function
  
    inline int view() {
        printf("inner: local_var = %d\n", local_var);
	local_var += 1;
        return local_var;
    }
  
    printf("outer: local_var = %d\n", local_var);

    return 0;
}
