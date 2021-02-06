package com.music.friends.app.business;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.music.friends.app.dto.NoticeDTO;
import com.music.friends.app.dto.NoticeMessageDTO;
import com.music.friends.app.exception.CustomException;
import com.music.friends.app.exception.ExceptionEnum;
import com.music.friends.app.pojo.Notice;
import com.music.friends.app.pojo.User;
import com.music.friends.app.service.NoticeService;
import com.music.friends.app.service.UserService;
import com.music.friends.app.utils.BeanListUtil;
import com.music.friends.app.utils.SpringSecurityUtil;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Component
public class NoticeBusiness {

    @Resource
    private NoticeService noticeService;
    @Resource
    private UserService userService;
    @Resource
    private UnConcernBusiness unConcernBusiness;
    @Resource
    private NoticeMessageBusiness noticeMessageBusiness;

    public Boolean insert(NoticeDTO noticeDTO) throws CustomException{
        if (noticeDTO == null){
            throw  new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        User user = userService.selectByUserName(SpringSecurityUtil.getUserName());
        if (user == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        Notice notice = BeanUtil.toBean(noticeDTO, Notice.class);
        notice.setUserId(user.getId());
        boolean noticeFlag = noticeService.insert(notice);
        List<String> fansIdList = unConcernBusiness.selectAllFansId(user.getId());
        List<NoticeMessageDTO> noticeMessages = new ArrayList<>();
        fansIdList.forEach(id -> {
            NoticeMessageDTO noticeMessage = new NoticeMessageDTO();
            noticeMessage.setTitle(noticeDTO.getTitle());
            noticeMessage.setContent(noticeDTO.getContent());
            noticeMessage.setUserId(id);
            noticeMessages.add(noticeMessage);
        });
        try {
            noticeMessageBusiness.batchInsert(noticeMessages);
        } catch (CustomException ignored) {}
        return noticeFlag;
    }

    public Boolean delete(String id) throws CustomException{
        if (StrUtil.hasBlank(id)){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        return noticeService.delete(id);
    }

    public Map<String, Object> listForPage(NoticeDTO noticeDTO) throws CustomException{
        if (noticeDTO == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        Notice notice = BeanUtil.toBean(noticeDTO, Notice.class);
        Map<String, Object> map = noticeService.listForPage(notice, noticeDTO.getPageNum(), noticeDTO.getPageSize());
        List<Notice> notices = (List<Notice>) map.get("list");
        map.put("list", BeanListUtil.toBeanList(notices, NoticeDTO.class));
        return map;
    }
}
