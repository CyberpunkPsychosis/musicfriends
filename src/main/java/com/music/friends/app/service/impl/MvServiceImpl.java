package com.music.friends.app.service.impl;

import cn.hutool.core.util.IdUtil;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import com.music.friends.app.dao.MvMapper;
import com.music.friends.app.pojo.Mv;
import com.music.friends.app.service.MvService;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class MvServiceImpl implements MvService {

    @Resource
    private MvMapper mvMapper;

    @Override
    public Boolean insert(Mv mv) {
        mv.setCreateTime(new Date());
        mv.setId(IdUtil.simpleUUID());
        return mvMapper.insertSelective(mv) == 1;
    }

    @Override
    public Boolean delete(String id) {
        return mvMapper.deleteByPrimaryKey(id) == 1;
    }

    @Override
    public Mv selectById(String id) {
        return mvMapper.selectByPrimaryKey(id);
    }

    @Override
    public Map<String, Object> listForPage(Mv mv, Integer pageNum, Integer pageSize) {
        PageHelper.offsetPage(pageNum, pageSize);
        List<Mv> mvs = mvMapper.selectAll(mv);
        PageInfo<Mv> pageInfo = new PageInfo<>(mvs);
        Map<String, Object> map = new HashMap<>();
        map.put("list", pageInfo.getList());
        map.put("total", pageInfo.getTotal());
        return map;
    }
}
