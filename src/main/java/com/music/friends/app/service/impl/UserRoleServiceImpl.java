package com.music.friends.app.service.impl;

import com.music.friends.app.dao.UserRoleMapper;
import com.music.friends.app.pojo.UserRole;
import com.music.friends.app.service.UserRoleService;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;

@Service
public class UserRoleServiceImpl implements UserRoleService {

    @Resource
    private UserRoleMapper userRoleMapper;

    @Override
    public Boolean update(UserRole userRole) {
        return userRoleMapper.updateByPrimaryKeySelective(userRole) == 1;
    }

    @Override
    public UserRole selectByUserId(String userId) {
        return userRoleMapper.selectByUserId(userId);
    }
}
