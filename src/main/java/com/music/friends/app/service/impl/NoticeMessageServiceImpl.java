package com.music.friends.app.service.impl;

import cn.hutool.core.util.IdUtil;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import com.music.friends.app.dao.NoticeMessageMapper;
import com.music.friends.app.pojo.NoticeMessage;
import com.music.friends.app.service.NoticeMessageService;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class NoticeMessageServiceImpl implements NoticeMessageService {

    @Resource
    private NoticeMessageMapper noticeMessageMapper;


    @Override
    public Boolean batchInsert(List<NoticeMessage> list) {
        list.forEach(x -> {
            x.setId(IdUtil.simpleUUID());
            x.setCreateTime(new Date());
        });
        return noticeMessageMapper.batchInsert(list) >= 1;
    }

    @Override
    public Boolean delete(String id) {
        return noticeMessageMapper.deleteByPrimaryKey(id) == 1;
    }

    @Override
    public Map<String, Object> listForPage(NoticeMessage noticeMessage, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<NoticeMessage> list = noticeMessageMapper.selectAll(noticeMessage);
        PageInfo<NoticeMessage> pageInfo = new PageInfo<>(list);
        Map<String, Object> map = new HashMap<>();
        map.put("list", pageInfo.getList());
        map.put("total", pageInfo.getTotal());
        return map;
    }
}
