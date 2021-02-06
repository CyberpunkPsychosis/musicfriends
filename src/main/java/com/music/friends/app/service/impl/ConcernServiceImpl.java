package com.music.friends.app.service.impl;

import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import com.music.friends.app.dao.ConcernMapper;
import com.music.friends.app.pojo.Concern;
import com.music.friends.app.service.ConcernService;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class ConcernServiceImpl implements ConcernService {
    @Resource
    private ConcernMapper concernMapper;

    @Override
    public Boolean insert(Concern concern) {
        concern.setCreateTime(new Date());
        return concernMapper.insertSelective(concern) == 1;
    }

    @Override
    public Boolean delete(String me, String other) {
        return concernMapper.deleteByPrimaryKey(me, other) == 1;
    }

    @Override
    public Concern selectById(String me, String other) {
        return concernMapper.selectByPrimaryKey(me, other);
    }

    @Override
    public Map<String, Object> listForPage(Concern concern, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<Concern> concerns = concernMapper.selectAll(concern);
        PageInfo<Concern> pageInfo = new PageInfo<>(concerns);
        Map<String, Object> map = new HashMap<>();
        map.put("list", pageInfo.getList());
        map.put("total", pageInfo.getTotal());
        return map;
    }
}
