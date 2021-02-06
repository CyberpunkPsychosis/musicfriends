package com.music.friends.app.service.impl;

import cn.hutool.core.util.IdUtil;
import com.music.friends.app.dao.UserInfoMapper;
import com.music.friends.app.pojo.UserInfo;
import com.music.friends.app.service.UserInfoService;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.Date;

@Service
public class UserInfoServiceImpl implements UserInfoService {
    @Resource
    private UserInfoMapper userInfoMapper;


    @Override
    public Boolean delete(String id) {
        return userInfoMapper.deleteByPrimaryKey(id) == 1;
    }

    @Override
    public Boolean insert(UserInfo userInfo) {
        userInfo.setId(IdUtil.simpleUUID());
        userInfo.setCreateTime(new Date());
        return userInfoMapper.insertSelective(userInfo) == 1;
    }

    @Override
    public UserInfo selectByUserId(String userId) {
        return userInfoMapper.selectByUserId(userId);
    }

    @Override
    public Boolean update(UserInfo userInfo) {
        userInfo.setUpdateTime(new Date());
        return userInfoMapper.updateByPrimaryKeySelective(userInfo) == 1;
    }
}
