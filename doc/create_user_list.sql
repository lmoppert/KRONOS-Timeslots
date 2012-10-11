# vim:syn=mysql
DROP TABLE user_list;
CREATE TABLE user_list AS (
    SELECT u.username, u.first_name, u.last_name, u.email, u.is_staff, u.is_active, p.* 
    FROM `auth_user` u 
    JOIN `timeslots_userprofile` p
    WHERE u.id = p.user_id 
);

