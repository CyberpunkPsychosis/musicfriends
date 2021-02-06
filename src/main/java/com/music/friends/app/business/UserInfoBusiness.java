package com.music.friends.app.business;

import cn.hutool.core.bean.BeanUtil;
import com.music.friends.app.dto.UserInfoDTO;
import com.music.friends.app.exception.CustomException;
import com.music.friends.app.exception.ExceptionEnum;
import com.music.friends.app.pojo.User;
import com.music.friends.app.pojo.UserInfo;
import com.music.friends.app.service.UserInfoService;
import com.music.friends.app.service.UserService;
import com.music.friends.app.utils.SpringSecurityUtil;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;

@Component
public class UserInfoBusiness {
    @Resource
    private UserInfoService userInfoService;
    @Resource
    private UserService userService;

    /**
     * 根据用户主键查询用户信息
     */
    public UserInfoDTO select() throws CustomException {
        String username = SpringSecurityUtil.getUserName();
        if (username == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        User user = userService.selectByUserName(username);
        if (user == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        UserInfo userInfo = userInfoService.selectByUserId(user.getId());
        return BeanUtil.toBean(userInfo, UserInfoDTO.class);
    }

}
