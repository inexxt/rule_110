#include <stdio.h>
#include <math.h>

#define FSIZE 145036570
#define magic_const_len 14

const char magic_const[] = {0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0};

char fname[256];
char buf[2][FSIZE];

int main()
{
  FILE *latfile;

  sprintf(fname,"%s","bigrow2.np");
  latfile=fopen(fname,"r");
  
  fread(&(buf[0][0]),sizeof(char),FSIZE,latfile);
  fclose(latfile);

  int i = 0;
  int sum = 0;
  for (i = 0; i < FSIZE; i++) {
    sum+= buf[0][i];
  }
  printf("Sum %d\n", sum);

  int epoch = 0;
  for (epoch = 0; epoch < 100000; epoch++) {
    printf("EPOCH %d\n", epoch);
    int i;
    for (i = epoch + 1; i < FSIZE - epoch; i++) {
      int par = epoch % 2;
      int npar = (par + 1) % 2;    
      buf[npar][i] = (buf[par][i] * buf[par][i+1]) * (1 - (buf[par][i] * buf[par][i+1] * buf[par][i-1]));
      if(i >= 13 + epoch) {
        char* point = &(buf[npar][i]);
        if (*(point) == 0 &&
            *(point - 1) == 0 &&
            *(point - 2) == 0 &&
            *(point - 3) == 1 &&

            *(point - 4) == 0 &&
            *(point - 5) == 1 &&
            *(point - 6) == 1 &&
            *(point - 7) == 0 &&

            *(point - 8) == 0 &&
            *(point - 9) == 1 &&
            *(point - 10) == 0 &&
            *(point - 11) == 1 &&

            *(point - 12) == 1 &&
            *(point - 13) == 0) {
          printf("STOPPED\n");
          return 0;
        }
        // char cond = true;
        // int k = 0;
        // for (k =0; k <= magic_const_len; k++) {
        //   if(*(point - k) != magic_const[magic_const_len - k - 1]) {
        //     cond = false;
        //   }
        // }
        // if(cond) {
        //   printf("STOPPED\n");
        //   return 0;
        // }
      }
    }
  }
  printf("DIDNT STOP\n");
  return 0;
}