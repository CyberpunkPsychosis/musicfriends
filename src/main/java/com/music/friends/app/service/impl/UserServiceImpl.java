package com.music.friends.app.service.impl;

import cn.hutool.core.util.IdUtil;
import com.music.friends.app.dao.UserMapper;
import com.music.friends.app.pojo.User;
import com.music.friends.app.service.UserService;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.Date;

/**
 * 用户实现类
 */
@Service
public class UserServiceImpl implements UserService {
    @Resource
    private UserMapper userMapper;

    @Override
    public Boolean insert(User user){
        user.setId(IdUtil.simpleUUID());
        user.setCreateTime(new Date());
        return userMapper.insertSelective(user) == 1;
    }

    @Override
    public Boolean delete(String id){
        return userMapper.deleteByPrimaryKey(id) == 1;
    }

    @Override
    public Boolean update(User user){
        user.setUpdateTime(new Date());
        return userMapper.updateByPrimaryKeySelective(user) == 1;
    }

    @Override
    public User selectById(String id){
        return userMapper.selectByPrimaryKey(id);
    }

    @Override
    public User selectByUserName(String username) {
        return userMapper.selectByUserName(username);
    }
}
