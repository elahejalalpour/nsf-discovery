drop table if exists VNF;
drop table if exists Host;
drop table if exists Chain;

create table if not exists VNF
					 (Con_id text, Con_name text, Host_name text, 
					  VNF_ip text, VNF_status text, VNF_type text, 
					  Chain_name text);
delete from VNF;

create table if not exists Host
					 (Host_name text, Host_ip text, Host_cpu real, 
					  Host_total_mem integer,Host_avail_mem integer, 
					  Host_used_mem integer,Last_seen integer, Active integer);
delete from Host;

create table if not exists Chain (Chain_anme text, Chain_type text);
delete from Chain;
