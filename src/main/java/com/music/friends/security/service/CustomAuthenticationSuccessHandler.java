package com.music.friends.security.service;

import cn.hutool.json.JSONUtil;
import com.music.friends.app.dao.UserMapper;
import com.music.friends.app.pojo.User;
import com.music.friends.app.utils.JwtUtil;
import com.music.friends.app.utils.ResponseGenerator;
import com.music.friends.app.utils.SpringSecurityUtil;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.SavedRequestAwareAuthenticationSuccessHandler;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

@Service
public class CustomAuthenticationSuccessHandler extends SavedRequestAwareAuthenticationSuccessHandler {

    @Resource
    private UserMapper userMapper;

    @Override
    public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response, Authentication authentication) throws ServletException, IOException {
        response.setCharacterEncoding("utf-8");
        response.setContentType("application/json; charset=utf-8");
        User user = userMapper.selectByUserName(SpringSecurityUtil.getUserName());
        String token = JwtUtil.createJWT(604800000, user);
        response.getWriter().print(JSONUtil.parse(ResponseGenerator.getSuccessResult("token", token)));
    }
}
