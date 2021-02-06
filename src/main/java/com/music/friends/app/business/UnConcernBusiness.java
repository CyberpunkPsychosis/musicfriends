package com.music.friends.app.business;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.music.friends.app.dto.UnConcernDTO;
import com.music.friends.app.exception.CustomException;
import com.music.friends.app.exception.ExceptionEnum;
import com.music.friends.app.pojo.UnConcern;
import com.music.friends.app.service.UnConcernService;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Component
public class UnConcernBusiness {
    @Resource
    private UnConcernService unConcernService;

    public Boolean insert(UnConcernDTO unConcernDTO) throws CustomException {
        if (unConcernDTO == null){
            throw  new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        UnConcern unConcern = BeanUtil.toBean(unConcernDTO, UnConcern.class);
        return unConcernService.insert(unConcern);
    }

    public Boolean delete(String me, String other) throws CustomException{
        if (StrUtil.hasBlank(me) || StrUtil.hasBlank(other)){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        return unConcernService.delete(me, other);
    }

    public Map<String, Object> selectAll(UnConcernDTO unConcernDTO) throws CustomException{
        if (unConcernDTO == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        UnConcern unConcern = BeanUtil.toBean(unConcernDTO, UnConcern.class);
        Map<String, Object> map = unConcernService.listForPage(unConcern, unConcernDTO.getPageNum(), unConcernDTO.getPageSize());
        List<UnConcern> concerns = (List<UnConcern>) map.get("list");
        map.put("list", concerns);
        return map;
    }

    public List<String> selectAllFansId(String userId) throws CustomException{
        if (StrUtil.hasBlank(userId)){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        List<UnConcern> list = unConcernService.selectAllFans(userId);
        return list.stream().map(UnConcern::getMe).collect(Collectors.toList());
    }
}
