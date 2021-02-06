package com.music.friends.app.service.impl;

import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import com.music.friends.app.dao.UnConcernMapper;
import com.music.friends.app.pojo.UnConcern;
import com.music.friends.app.service.UnConcernService;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class UnConcernServiceImpl implements UnConcernService {

    @Resource
    private UnConcernMapper unConcernMapper;

    @Override
    public Boolean insert(UnConcern unConcern) {
        unConcern.setCreateTime(new Date());
        return unConcernMapper.insertSelective(unConcern) == 1;
    }

    @Override
    public Boolean delete(String me, String other) {
        return unConcernMapper.deleteByPrimaryKey(me, other) == 1;
    }

    @Override
    public Map<String, Object> listForPage(UnConcern unConcern, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<UnConcern> unConcerns = unConcernMapper.selectAll(unConcern);
        PageInfo<UnConcern> pageInfo = new PageInfo<>(unConcerns);
        Map<String, Object> map = new HashMap<>();
        map.put("list", pageInfo.getList());
        map.put("total", pageInfo.getTotal());
        return map;
    }

    @Override
    public List<UnConcern> selectAllFans(String userId) {
        return unConcernMapper.selectAllFans(userId);
    }
}
