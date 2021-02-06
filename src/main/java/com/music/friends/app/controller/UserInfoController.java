package com.music.friends.app.controller;

import com.music.friends.app.business.UserInfoBusiness;
import com.music.friends.app.dto.UserInfoDTO;
import com.music.friends.app.exception.CustomException;
import com.music.friends.app.utils.ResponseGenerator;
import com.music.friends.app.utils.ResponseResult;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;

@RestController
@RequestMapping("userInfo")
public class UserInfoController {
    @Resource
    private UserInfoBusiness userInfoBusiness;

    @PostMapping("getUserInfo")
    @PreAuthorize("hasAuthority('/userInfo/getUserInfo')")
    public ResponseResult getUserInfo(){
        try {
            UserInfoDTO userInfoDTO = userInfoBusiness.select();
            return ResponseGenerator.getSuccessResult("item", userInfoDTO);
        } catch (CustomException e) {
            e.printStackTrace();
            return ResponseGenerator.getFailResult(e.getMessage());
        }
    }
}
