package com.music.friends.app.business;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.music.friends.app.dto.ConcernDTO;
import com.music.friends.app.exception.CustomException;
import com.music.friends.app.exception.ExceptionEnum;
import com.music.friends.app.pojo.Concern;
import com.music.friends.app.service.ConcernService;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.List;
import java.util.Map;

@Component
public class ConcernBusiness {

    @Resource
    private ConcernService concernService;

    public Boolean insert(ConcernDTO concernDTO) throws CustomException {
        if (concernDTO == null){
            throw  new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        Concern concern = BeanUtil.toBean(concernDTO, Concern.class);
        return concernService.insert(concern);
    }

    public Boolean delete(String me, String other) throws CustomException{
        if (StrUtil.hasBlank(me) || StrUtil.hasBlank(other)){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        return concernService.delete(me, other);
    }

    public Map<String, Object> listForPage(ConcernDTO concernDTO) throws CustomException{
        if (concernDTO == null){
            throw new CustomException(ExceptionEnum.PARAM_NULL_EXCEPTION);
        }
        Concern concern = BeanUtil.toBean(concernDTO, Concern.class);
        Map<String, Object> map = concernService.listForPage(concern, concernDTO.getPageNum(), concernDTO.getPageSize());
        List<Concern> concerns = (List<Concern>) map.get("list");
        map.put("list", concerns);
        return map;
    }

}
