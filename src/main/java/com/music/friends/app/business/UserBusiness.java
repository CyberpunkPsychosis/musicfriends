package com.music.friends.app.business;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.music.friends.app.dto.UserDTO;
import com.music.friends.app.exception.CustomException;
import com.music.friends.app.exception.ExceptionEnum;
import com.music.friends.app.pojo.User;
import com.music.friends.app.service.UserService;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;

@Component
public class UserBusiness {

    @Resource
    private UserService userService;

    public Boolean insert(UserDTO userDTO) throws CustomException{
        if (userDTO == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        User user = BeanUtil.toBean(userDTO, User.class);
        return userService.insert(user);
    }

    public Boolean delete(UserDTO userDTO) throws CustomException{
        if (StrUtil.hasBlank(userDTO.getId())){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        return userService.delete(userDTO.getId());
    }

    public Boolean update(UserDTO userDTO) throws CustomException{
        if (userDTO == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        User user = BeanUtil.toBean(userDTO, User.class);
        return userService.update(user);
    }

    public UserDTO selectById(UserDTO userDTO) throws CustomException{
        if (StrUtil.hasBlank(userDTO.getId())){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        User user = userService.selectById(userDTO.getId());
        if (user == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        return BeanUtil.toBean(user, UserDTO.class);
    }

    public UserDTO selectByUserName(UserDTO userDTO) throws CustomException{
        if (userDTO == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        User user = userService.selectByUserName(userDTO.getAccount());
        if (user == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        return BeanUtil.toBean(user, UserDTO.class);
    }

}
