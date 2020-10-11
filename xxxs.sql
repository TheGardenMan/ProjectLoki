create or replace function public_posts_first(post_req_sender_id integer)
  returns table (user_id_ integer,public_post_id_ integer,views_ integer,likes_ integer,dislikes_ integer)
as
$$
declare
	last_location_ geography;
begin
	select last_location into last_location_ from user_last_location where user_id=post_req_sender_id;
	return query select user_id,public_post_id,views,likes,dislikes from public_posts WHERE ST_DWithin(public_post_location,last_location_, 5000) order by public_post_time desc limit 20;
end;
$$
language plpgsql;

select public_posts_first(121);