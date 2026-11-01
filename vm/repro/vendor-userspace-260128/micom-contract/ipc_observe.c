/* VM read-only observer: exact Qt-derived key files, never create/reset IPC. */
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/sem.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
int main(void) {
 const char *paths[]={
 "/tmp/qipc_sharedmemory_MICOMSTATUSMESSAGEea9b2c48d97ddb319dd9ac9fa4f70206a8ccd52c",
 "/tmp/qipc_systemsem_MICOMSTATUSMESSAGEea9b2c48d97ddb319dd9ac9fa4f70206a8ccd52c"};
 for(int i=0;i<2;i++) {
  key_t k=ftok(paths[i],'Q');
  if(k==(key_t)-1){printf("IPC_OBSERVE kind=%s ftok_error=%s\n",i?"sem":"shm",strerror(errno));continue;}
  printf("IPC_OBSERVE kind=%s key=0x%08x ",i?"sem":"shm",(unsigned)k);
  if(i){int id=semget(k,1,0); if(id<0){printf("error=%s\n",strerror(errno));continue;}
   printf("id=%d val=%d last_pid=%d waiting=%d zero_waiting=%d\n",id,semctl(id,0,GETVAL),semctl(id,0,GETPID),semctl(id,0,GETNCNT),semctl(id,0,GETZCNT));
  } else {int id=shmget(k,1,0); struct shmid_ds ds;
   if(id<0||shmctl(id,IPC_STAT,&ds)<0){printf("error=%s\n",strerror(errno));continue;}
   printf("id=%d size=%lu creator=%d last_pid=%d attachments=%lu mode=%o\n",id,(unsigned long)ds.shm_segsz,ds.shm_cpid,ds.shm_lpid,(unsigned long)ds.shm_nattch,ds.shm_perm.mode);
   if(ds.shm_segsz!=35){puts("IPC_OBSERVE unexpected_size_refuse_read");continue;}
   const unsigned char *p=shmat(id,0,SHM_RDONLY);
   if(p==(void*)-1){printf("IPC_OBSERVE shmat_error=%s\n",strerror(errno));continue;}
   /* No lock acquired: diagnostic snapshot may race; not an atomic payload claim. */
   printf("IPC_OBSERVE non_atomic_hex=");for(int n=0;n<35;n++)printf("%02x",p[n]);puts("");shmdt(p);
  }
 }
 return 0;
}
