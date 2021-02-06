package com.music.friends.app.service.impl;

import cn.hutool.core.util.IdUtil;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import com.music.friends.app.dao.MusicMapper;
import com.music.friends.app.pojo.Music;
import com.music.friends.app.service.MusicService;
import com.music.friends.app.utils.SpringSecurityUtil;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class MusicServiceImpl implements MusicService {
    @Resource
    private MusicMapper musicMapper;

    @Override
    public Boolean insert(Music music) {
        music.setCreateTime(new Date());
        music.setId(IdUtil.simpleUUID());
        return musicMapper.insertSelective(music) == 1;
    }

    @Override
    public Boolean delete(String id) {
        return musicMapper.deleteByPrimaryKey(id) == 1;
    }

    @Override
    public Boolean update(Music music) {
        return musicMapper.updateByPrimaryKeySelective(music) == 1;
    }

    @Override
    public Music selectById(String id) {
        return musicMapper.selectByPrimaryKey(id);
    }

    @Override
    public List<Music> selectAll() {
        return musicMapper.selectAll(new Music());
    }

    @Override
    public Map<String, Object> listForPage(Music music, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<Music> list = musicMapper.selectAll(music);
        PageInfo<Music> pageInfo = new PageInfo<>(list);
        Map<String, Object> map = new HashMap<>();
        map.put("list", pageInfo.getList());
        map.put("total", pageInfo.getTotal());
        return map;
    }
}
