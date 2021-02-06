package com.music.friends.app.business;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.music.friends.app.dto.MvDTO;
import com.music.friends.app.exception.CustomException;
import com.music.friends.app.exception.ExceptionEnum;
import com.music.friends.app.pojo.Mv;
import com.music.friends.app.pojo.User;
import com.music.friends.app.service.MvService;
import com.music.friends.app.service.UserService;
import com.music.friends.app.utils.AlibabaOSSUtil;
import com.music.friends.app.utils.BeanListUtil;
import com.music.friends.app.utils.SpringSecurityUtil;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.List;
import java.util.Map;

@Component
public class MvBusiness {

    @Resource
    private MvService mvService;
    @Resource
    private UserService userService;

    public Boolean insert(MvDTO mvDTO) throws CustomException{
        if (mvDTO == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        User user = userService.selectByUserName(SpringSecurityUtil.getUserName());
        if (user == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        Mv mv = BeanUtil.toBean(mvDTO, Mv.class);
        mv.setUserId(user.getId());
        return mvService.insert(mv);
    }

    public Boolean delete(String id) throws CustomException{
        if (StrUtil.hasBlank(id)){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        Mv mv = mvService.selectById(id);
        if (mv == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        AlibabaOSSUtil.delete(mv.getUrl());
        return mvService.delete(id);
    }

    public Map<String, Object> listForPage(MvDTO mvDTO) throws CustomException{
        if (mvDTO == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        Mv mv = BeanUtil.toBean(mvDTO, Mv.class);
        Map<String, Object> map = mvService.listForPage(mv, mvDTO.getPageNum(), mvDTO.getPageSize());
        List<Mv> list = (List<Mv>) map.get("list");
        map.put("list", BeanListUtil.toBeanList(list, MvDTO.class));
        return map;
    }

    public MvDTO select(String id) throws CustomException{
        if (StrUtil.hasBlank(id)){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        Mv mv = mvService.selectById(id);
        if (mv == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        return BeanUtil.toBean(mv, MvDTO.class);
    }
}
