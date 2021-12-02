

set enable_seqscan=off;

insert into t1 values (1,10);
select lsm3_start_merge('lsm3_index');
select lsm3_wait_merge_completion('lsm3_index');
insert into t1 values (2,20);
select lsm3_start_merge('lsm3_index');
select lsm3_wait_merge_completion('lsm3_index');
insert into t1 values (3,30);
select lsm3_start_merge('lsm3_index');
select lsm3_wait_merge_completion('lsm3_index');
insert into t1 values (4,40);
select lsm3_start_merge('lsm3_index');
select lsm3_wait_merge_completion('lsm3_index');
insert into t1 values (5,50);
select lsm3_start_merge('lsm3_index');
select lsm3_wait_merge_completion('lsm3_index');
select lsm3_get_merge_count('lsm3_index');
select * from t1 where k = 1;
select * from t1 order by k;
select * from t1 order by k desc;
explain (COSTS OFF, TIMING OFF, SUMMARY OFF) select * from t1 order by k;

insert into t1 values (generate_series(1,100000), 1);
insert into t1 values (generate_series(1000001,200000), 2);
insert into t1 values (generate_series(2000001,300000), 3);
insert into t1 values (generate_series(1,100000), 1);
insert into t1 values (generate_series(1000001,200000), 2);
insert into t1 values (generate_series(2000001,300000), 3);
select * from t1 where k = 1;
select * from t1 where k = 1000000;
select * from t1 where k = 2000000;
select * from t1 where k = 3000000;
explain (COSTS OFF, TIMING OFF, SUMMARY OFF) select * from t1 where k = 1;
select lsm3_get_merge_count('lsm3_index') > 5;

truncate table t1;
insert into t1 values (generate_series(1,1000000), 1);
select * from t1 where k = 1;

reindex table t1;
select * from t1 where k = 1;

drop table t1;

create table lsm(k bigint);
insert into lsm values (generate_series(1, 1000000));
create index concurrently on lsm using lsm3(k);
select * from lsm where k = 1;

drop table lsm;
