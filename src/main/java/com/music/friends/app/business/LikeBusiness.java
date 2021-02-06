package com.music.friends.app.business;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.music.friends.app.dto.IdeaDTO;
import com.music.friends.app.dto.LikeDTO;
import com.music.friends.app.dto.MusicDTO;
import com.music.friends.app.dto.MvDTO;
import com.music.friends.app.exception.CustomException;
import com.music.friends.app.exception.ExceptionEnum;
import com.music.friends.app.pojo.Like;
import com.music.friends.app.pojo.User;
import com.music.friends.app.pojo.UserRole;
import com.music.friends.app.service.LikeService;
import com.music.friends.app.service.UserRoleService;
import com.music.friends.app.service.UserService;
import com.music.friends.app.utils.SpringSecurityUtil;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;

@Component
public class LikeBusiness {

    @Resource
    private LikeService likeService;
    @Resource
    private UserService userService;
    @Resource
    private UserRoleService userRoleService;
    @Resource
    private MusicBusiness musicBusiness;
    @Resource
    private IdeaBusiness ideaBusiness;
    @Resource
    private MvBusiness mvBusiness;

    public Boolean insertIdea(LikeDTO likeDTO) throws CustomException{
        if (likeDTO == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        User user = userService.selectByUserName(SpringSecurityUtil.getUserName());
        if (user == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        Like like = BeanUtil.toBean(likeDTO, Like.class);
        like.setUserId(user.getId());
        like.setType(1);
        IdeaDTO ideaDTO = ideaBusiness.selectById(likeDTO.getLikeId());
        like.setLikedUserId(ideaDTO.getUserId());
        boolean likeFlag = likeService.insert(like);
        Integer countLike = likeService.count(user.getId(), ideaDTO.getUserId());
        Integer countLiked = likeService.count(ideaDTO.getUserId(), user.getId());
        if (countLike == 20 && countLiked == 20){
            // TODO: 2020/11/22 邮箱发送对方微信号 
        }
        return likeFlag;
    }

    public Boolean insertMusic(LikeDTO likeDTO) throws CustomException{
        if (likeDTO == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        User user = userService.selectByUserName(SpringSecurityUtil.getUserName());
        if (user == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        Like like = BeanUtil.toBean(likeDTO, Like.class);
        like.setUserId(user.getId());
        like.setType(2);
        MusicDTO musicDTO = musicBusiness.select(likeDTO.getLikeId());
        like.setLikedUserId(musicDTO.getUserId());
        boolean likeFlag = likeService.insert(like);
        Integer integer = likeService.count(likeDTO.getLikeId());
        if (integer == 1000){
            UserRole userRole = userRoleService.selectByUserId(musicDTO.getUserId());
            if (userRole == null){
                throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
            }
            userRole.setRoleId("star");
            userRoleService.update(userRole);
        }
        return likeFlag;
    }

    public Boolean insertMv(LikeDTO likeDTO) throws CustomException{
        if (likeDTO == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        User user = userService.selectByUserName(SpringSecurityUtil.getUserName());
        if (user == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        Like like = BeanUtil.toBean(likeDTO, Like.class);
        like.setUserId(user.getId());
        like.setType(3);
        MvDTO mvDTO = mvBusiness.select(likeDTO.getLikeId());
        like.setLikedUserId(mvDTO.getUserId());
        return likeService.insert(like);
    }

    public Boolean delete(String likeId, String userId) throws CustomException{
        if (StrUtil.hasBlank(likeId) || StrUtil.hasBlank(userId)){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        return likeService.delete(likeId, userId);
    }
}
