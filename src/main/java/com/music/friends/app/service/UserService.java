package com.music.friends.app.service;

import com.music.friends.app.pojo.User;

/**
 * 用户Service
 * @author yum
 */
public interface UserService {

    Boolean insert(User user);

    Boolean delete(String id);

    Boolean update(User user);

    User selectById(String id);

    User selectByUserName(String username);
}
