begin;
truncate table followers;
truncate table follow_requests;
truncate table follow_requests_accepted;
end transaction;


select * from followers;
select * from follow_requests;
select * from follow_requests_accepted;

