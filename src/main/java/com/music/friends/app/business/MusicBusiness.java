package com.music.friends.app.business;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.music.friends.app.dto.MusicDTO;
import com.music.friends.app.exception.CustomException;
import com.music.friends.app.exception.ExceptionEnum;
import com.music.friends.app.pojo.Music;
import com.music.friends.app.pojo.User;
import com.music.friends.app.service.MusicService;
import com.music.friends.app.service.UserService;
import com.music.friends.app.utils.AlibabaOSSUtil;
import com.music.friends.app.utils.BeanListUtil;
import com.music.friends.app.utils.SpringSecurityUtil;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.List;
import java.util.Map;

@Component
public class MusicBusiness {
    @Resource
    private MusicService musicService;
    @Resource
    private UserService userService;

    public Boolean insert(MusicDTO musicDTO) throws CustomException {
        if (musicDTO == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        User user = userService.selectByUserName(SpringSecurityUtil.getUserName());
        if (user == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        Music music = BeanUtil.toBean(musicDTO, Music.class);
        music.setUserId(user.getId());
        return musicService.insert(music);
    }

    public Boolean delete(String id) throws CustomException{
        if (StrUtil.hasBlank(id)){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        Music music = musicService.selectById(id);
        if (music == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        AlibabaOSSUtil.delete(music.getUrl());
        return musicService.delete(id);
    }

    public Map<String, Object> listForPage(MusicDTO musicDTO) throws CustomException{
        if (musicDTO == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        Music music = BeanUtil.toBean(musicDTO, Music.class);
        Map<String, Object> map = musicService.listForPage(music, musicDTO.getPageNum(), musicDTO.getPageSize());
        List<Music> list = (List<Music>) map.get("list");
        map.put("list", BeanListUtil.toBeanList(list, MusicDTO.class));
        return map;
    }

    public MusicDTO select(String id) throws CustomException{
        if (StrUtil.hasBlank(id)){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        Music music = musicService.selectById(id);
        if (music == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        return BeanUtil.toBean(music, MusicDTO.class);
    }
}
