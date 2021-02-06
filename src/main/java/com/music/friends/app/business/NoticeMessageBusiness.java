package com.music.friends.app.business;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.music.friends.app.dto.NoticeMessageDTO;
import com.music.friends.app.exception.CustomException;
import com.music.friends.app.exception.ExceptionEnum;
import com.music.friends.app.pojo.NoticeMessage;
import com.music.friends.app.service.NoticeMessageService;
import com.music.friends.app.utils.BeanListUtil;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.List;
import java.util.Map;

@Component
public class NoticeMessageBusiness {

    @Resource
    private NoticeMessageService noticeMessageService;

    public Boolean batchInsert(List<NoticeMessageDTO> list) throws CustomException {
        if (list.size() == 0){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        List<NoticeMessage> noticeMessages = BeanListUtil.toBeanList(list, NoticeMessage.class);
        return noticeMessageService.batchInsert(noticeMessages);
    }

    public Boolean delete(String id) throws CustomException{
        if (StrUtil.hasBlank(id)){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        return noticeMessageService.delete(id);
    }

    public Map<String, Object> listForPage(NoticeMessageDTO noticeMessageDTO) throws CustomException{
        if (noticeMessageDTO == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        NoticeMessage noticeMessage = BeanUtil.toBean(noticeMessageDTO, NoticeMessage.class);
        Map<String, Object> map = noticeMessageService.listForPage(noticeMessage, noticeMessageDTO.getPageNum(), noticeMessageDTO.getPageSize());
        List<NoticeMessage> list = (List<NoticeMessage>) map.get("list");
        map.put("list", BeanListUtil.toBeanList(list, NoticeMessageDTO.class));
        return map;
    }
}
