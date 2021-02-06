package com.music.friends.app.service;

import com.music.friends.app.pojo.UserRole;

public interface UserRoleService {

    Boolean update(UserRole userRole);

    UserRole selectByUserId(String userId);
}
