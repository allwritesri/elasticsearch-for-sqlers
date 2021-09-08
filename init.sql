CREATE TABLE account (
	user_id serial PRIMARY KEY,
	username VARCHAR ( 50 ) UNIQUE NOT NULL,
	password VARCHAR ( 50 ) NOT NULL,
	email VARCHAR ( 255 ) UNIQUE NOT NULL,
	phone VARCHAR ( 255 ) UNIQUE NOT NULL,
	created_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tweet (
	tweet_id serial,
	tweet_text VARCHAR ( 255 ) NOT NULL,
	user_id int NOT NULL,
	created_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id)
      REFERENCES account(user_id),
  PRIMARY KEY(tweet_id, user_id)
);


insert into account(username,password,email,phone) values('JOHN','JOHN','JOHN@gmail.com','123456789');
insert into account(username,password,email,phone) values('Kumar','Ram','kumar@gmail.com','123456789');


insert into tweet(tweet_text,user_id) values('Hello!',1);
insert into tweet(tweet_text,user_id) values('Good Morning',1);
insert into tweet(tweet_text,user_id) values('Today is a nice day',1);


/*using JOIN*/
select tweet_id,tweet_text, t.user_id, t.created_date
from tweet t join account a on t.user_id=a.user_id and a.username='JOHN';
/*using inner query*/
select * from tweet t
where t.user_id = (select a.user_id  from account a where a.username='JOHN');


create or replace function concatFirstAndLastName(first_name varchar(256), last_name varchar(256)) returns varchar as
'$$

Begin

return first_name+last_name;

End;

$$
'

Language 'plpgsql';