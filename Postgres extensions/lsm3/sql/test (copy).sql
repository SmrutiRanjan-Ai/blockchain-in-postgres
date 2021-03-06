

create table t(k bigint, val bigint);
create index lsm3_index on t using lsm3(k);

set enable_seqscan=off;

insert into t values (1,10);
select lsm3_start_merge('lsm3_index');
select lsm3_wait_merge_completion('lsm3_index');
insert into t values (2,20);
select lsm3_start_merge('lsm3_index');
select lsm3_wait_merge_completion('lsm3_index');
insert into t values (3,30);
select lsm3_start_merge('lsm3_index');
select lsm3_wait_merge_completion('lsm3_index');
insert into t values (4,40);
select lsm3_start_merge('lsm3_index');
select lsm3_wait_merge_completion('lsm3_index');
insert into t values (5,50);
select lsm3_start_merge('lsm3_index');
select lsm3_wait_merge_completion('lsm3_index');
select lsm3_get_merge_count('lsm3_index');
select * from t where k = 1;
select * from t order by k;
select * from t order by k desc;
explain (COSTS OFF, TIMING OFF, SUMMARY OFF) select * from t order by k;

insert into t values (generate_series(1,100000), 1);

select * from t;


