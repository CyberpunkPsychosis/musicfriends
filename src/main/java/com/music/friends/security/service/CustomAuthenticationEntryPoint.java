package com.music.friends.security.service;

import cn.hutool.http.HttpStatus;
import cn.hutool.json.JSONUtil;
import com.music.friends.app.utils.ResponseResult;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.stereotype.Service;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

@Service
public class CustomAuthenticationEntryPoint implements AuthenticationEntryPoint {

    @Override
    public void commence(HttpServletRequest httpServletRequest, HttpServletResponse httpServletResponse, AuthenticationException e) throws IOException, ServletException {
        httpServletResponse.setCharacterEncoding("utf-8");
        httpServletResponse.setContentType("application/json; charset=utf-8");
        httpServletResponse.getWriter().print(JSONUtil.toJsonPrettyStr(new ResponseResult().setCode(HttpStatus.HTTP_UNAUTHORIZED).setMessage("未认证")));
    }
}
