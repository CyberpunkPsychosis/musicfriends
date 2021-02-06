package com.music.friends.app.controller;

import cn.hutool.http.HttpStatus;
import com.music.friends.app.business.IdeaBusiness;
import com.music.friends.app.dto.IdeaDTO;
import com.music.friends.app.exception.CustomException;
import com.music.friends.app.utils.ResponseGenerator;
import com.music.friends.app.utils.ResponseResult;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("idea")
public class IdeaController {
    @Resource
    private IdeaBusiness ideaBusiness;

    @PostMapping("insert")
    @PreAuthorize("hasAuthority('/idea/insert')")
    public ResponseResult insert(IdeaDTO ideaDTO){
        try {
            Boolean flag = ideaBusiness.insert(ideaDTO);
            if (flag){
                return ResponseGenerator.getSuccessResult();
            }else {
                return ResponseGenerator.getFailResult();
            }
        } catch (CustomException e) {
            e.printStackTrace();
            return ResponseGenerator.getFailResult(e.getMessage());
        }
    }

    @PostMapping("delete")
    @PreAuthorize("hasAuthority('/idea/delete')")
    public ResponseResult delete(IdeaDTO ideaDTO){
        try {
            Boolean flag = ideaBusiness.delete(ideaDTO.getId());
            if (flag){
                return ResponseGenerator.getSuccessResult();
            }else {
                return ResponseGenerator.getFailResult();
            }
        } catch (CustomException e) {
            e.printStackTrace();
            return ResponseGenerator.getFailResult(e.getMessage());
        }
    }

    @PostMapping("selectByMyself")
    @PreAuthorize("hasAuthority('/idea/selectByMyself')")
    public ResponseResult selectByMyself(){
        try {
            List<IdeaDTO> ideaDTOS = ideaBusiness.selectByMyself();
            return ResponseGenerator.getSuccessResult("list", ideaDTOS);
        } catch (CustomException e) {
            e.printStackTrace();
            return ResponseGenerator.getFailResult(e.getMessage());
        }
    }

    @PostMapping("selectAll")
    @PreAuthorize("hasAuthority('/idea/selectAll')")
    public ResponseResult selectAll(@RequestBody IdeaDTO ideaDTO){
        try {
            Map<String, Object> map = ideaBusiness.selectAll(ideaDTO.getPageNum(), ideaDTO.getPageSize());
            return new ResponseResult().setCode(HttpStatus.HTTP_OK)
                    .setMessage("success").setData("total", map.get("total"))
                    .setData("list", map.get("list"));
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseGenerator.getFailResult(e.getMessage());
        }
    }
}
