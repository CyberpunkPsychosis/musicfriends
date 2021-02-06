package com.music.friends.app.business;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.music.friends.app.dto.IdeaDTO;
import com.music.friends.app.exception.CustomException;
import com.music.friends.app.exception.ExceptionEnum;
import com.music.friends.app.pojo.Idea;
import com.music.friends.app.pojo.User;
import com.music.friends.app.service.IdeaService;
import com.music.friends.app.service.UserService;
import com.music.friends.app.utils.AlibabaOSSUtil;
import com.music.friends.app.utils.BeanListUtil;
import com.music.friends.app.utils.SpringSecurityUtil;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.List;
import java.util.Map;

@Component
public class IdeaBusiness {

    @Resource
    private IdeaService ideaService;
    @Resource
    private UserService userService;

    public Boolean delete(String id) throws CustomException{
        if (id == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        Idea idea = ideaService.selectById(id);
        if (idea == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        IdeaDTO ideaDTO = BeanUtil.toBean(idea, IdeaDTO.class);
        List<String> urls = ideaDTO.getPictures();
        AlibabaOSSUtil.batchDelete(urls, false);
        return ideaService.deleteByPrimaryKey(id);
    }

    public Boolean insert(IdeaDTO ideaDTO) throws CustomException{
        if (ideaDTO == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        Idea idea = BeanUtil.toBean(ideaDTO, Idea.class);
        User user = userService.selectByUserName(SpringSecurityUtil.getUserName());
        if (user == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        idea.setUserId(user.getId());
        return ideaService.insert(idea);
    }

    public List<IdeaDTO> selectByMyself() throws CustomException{
        User user = userService.selectByUserName(SpringSecurityUtil.getUserName());
        if (user == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        List<Idea> ideas = ideaService.selectByUserId(user.getId());
        return BeanListUtil.toBeanList(ideas, IdeaDTO.class);
    }

    /**
     * 查询所有公开的动态以及，好友的仅限好友可见的动态, 以及自己的仅限好友的状态
     * @return List<IdeaDTO>
     */
    public Map<String, Object> selectAll(Integer pageNum, Integer pageSize) throws CustomException{
        User user = userService.selectByUserName(SpringSecurityUtil.getUserName());
        if (user == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        Map<String, Object> map = ideaService.selectAllPublicFriendsMyself(user.getId(), pageNum, pageSize);
        List<Idea> list = (List<Idea>)map.get("list");
        map.put("list", BeanListUtil.toBeanList(list, IdeaDTO.class));
        return map;
    }

    public IdeaDTO selectById(String id) throws CustomException{
        if (StrUtil.hasBlank(id)){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        Idea idea = ideaService.selectById(id);
        if (idea == null){
            throw new CustomException(ExceptionEnum.DATA_NULL_EXCEPTION);
        }
        return BeanUtil.toBean(idea, IdeaDTO.class);
    }
}
