package com.music.friends.app.service;

import com.music.friends.app.pojo.UserInfo;

public interface UserInfoService {
    /**
     * 删除用户信息
     */
    Boolean delete(String id);

    /**
     * 插入用户信息
     */
    Boolean insert(UserInfo userInfo);

    /**
     * 根据Id查询用户信息
     */
    UserInfo selectByUserId(String userId);

    /**
     * 更行用户信息
     */
    Boolean update(UserInfo userInfo);
}
