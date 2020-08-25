begin;
truncate table followers;
truncate table follow_requests;
truncate table follow_requests_accepted;
end transaction;

a 8cc9d8b6f68bfbd5eb59a1e056b8a7de9bda138c 121
b c59f294a176cc9ba303a05d7e598d33492e87a57 122
c 4c7b68e11ee73d5d4067fd9ce1492d05724d205c 123
http://127.0.0.1:8000/
select * from followers;
select * from follow_requests;
select * from follow_requests_accepted;


