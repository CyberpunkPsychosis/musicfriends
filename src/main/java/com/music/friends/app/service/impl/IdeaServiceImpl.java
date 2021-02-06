package com.music.friends.app.service.impl;

import cn.hutool.core.util.IdUtil;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import com.music.friends.app.dao.IdeaMapper;
import com.music.friends.app.dto.IdeaDTO;
import com.music.friends.app.pojo.Idea;
import com.music.friends.app.service.IdeaService;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class IdeaServiceImpl implements IdeaService {

    @Resource
    private IdeaMapper ideaMapper;

    @Override
    public Boolean deleteByPrimaryKey(String id) {
        return ideaMapper.deleteByPrimaryKey(id) == 1;
    }

    @Override
    public Boolean insert(Idea idea) {
        idea.setCreateTime(new Date());
        idea.setId(IdUtil.simpleUUID());
        return ideaMapper.insertSelective(idea) == 1;
    }

    @Override
    public List<Idea> selectByUserId(String userId) {
        return ideaMapper.selectByUserId(userId);
    }

    @Override
    public Map<String, Object> selectAllPublicFriendsMyself(String userId, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<Idea> ideas = ideaMapper.selectAllPublicFriendsMyself(userId);
        PageInfo<Idea> pageInfo = new PageInfo<>(ideas);
        Map<String, Object> map = new HashMap<>();
        map.put("total", pageInfo.getTotal());
        map.put("list", pageInfo.getList());
        return map;
    }

    @Override
    public Idea selectById(String id) {
        return ideaMapper.selectByPrimaryKey(id);
    }
}
