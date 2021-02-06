package com.music.friends.app.service.impl;

import cn.hutool.core.util.IdUtil;
import com.music.friends.app.dao.LikeMapper;
import com.music.friends.app.pojo.Like;
import com.music.friends.app.service.LikeService;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.Date;

@Service
public class LikeServiceImpl implements LikeService {

    @Resource
    private LikeMapper likeMapper;

    @Override
    public Boolean insert(Like like) {
        like.setCreateTime(new Date());
        like.setId(IdUtil.simpleUUID());
        return likeMapper.insertSelective(like) == 1;
    }

    @Override
    public Integer count(String likeId) {
        return likeMapper.count(likeId);
    }

    @Override
    public Boolean delete(String likeId, String userId) {
        return likeMapper.delete(likeId, userId) == 1;
    }

    @Override
    public Integer count(String userId, String likedUserId) {
        return likeMapper.countByEachOther(userId, likedUserId);
    }
}
