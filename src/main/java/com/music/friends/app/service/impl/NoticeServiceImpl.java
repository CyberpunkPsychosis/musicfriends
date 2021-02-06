package com.music.friends.app.service.impl;

import cn.hutool.core.util.IdUtil;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import com.music.friends.app.dao.NoticeMapper;
import com.music.friends.app.pojo.Notice;
import com.music.friends.app.service.NoticeService;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class NoticeServiceImpl implements NoticeService {

    @Resource
    private NoticeMapper noticeMapper;

    @Override
    public Boolean insert(Notice notice) {
        notice.setId(IdUtil.simpleUUID());
        notice.setCreateTime(new Date());
        return noticeMapper.insertSelective(notice) == 1;
    }

    @Override
    public Boolean delete(String id) {
        return noticeMapper.deleteByPrimaryKey(id) == 1;
    }

    @Override
    public Map<String, Object> listForPage(Notice notice, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<Notice> notices = noticeMapper.selectAll(notice);
        PageInfo<Notice> pageInfo = new PageInfo<>(notices);
        Map<String, Object> map = new HashMap<>();
        map.put("list", pageInfo.getList());
        map.put("total", pageInfo.getTotal());
        return map;
    }
}
