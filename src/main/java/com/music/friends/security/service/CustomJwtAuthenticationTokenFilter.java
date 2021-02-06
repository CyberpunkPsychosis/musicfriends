package com.music.friends.security.service;

import cn.hutool.core.util.StrUtil;
import com.music.friends.app.dao.UserMapper;
import com.music.friends.app.pojo.User;
import com.music.friends.app.service.AuthorityService;
import com.music.friends.app.utils.JwtUtil;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Service;
import org.springframework.web.filter.OncePerRequestFilter;

import javax.annotation.Resource;
import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.List;

@Service
public class CustomJwtAuthenticationTokenFilter extends OncePerRequestFilter {
    @Resource
    private UserMapper userMapper;
    @Resource
    private AuthorityService authorityService;

    @Override
    protected void doFilterInternal(HttpServletRequest httpServletRequest, HttpServletResponse httpServletResponse, FilterChain filterChain) throws ServletException, IOException {
        String token = httpServletRequest.getHeader("Authorization");
        if (!StrUtil.hasBlank(token)){
            String username = JwtUtil.getUserName(token);
            if (StrUtil.hasBlank(username)){
                filterChain.doFilter(httpServletRequest, httpServletResponse);
                return;
            }
            User user = userMapper.selectByUserName(username);
            if (user == null){
                filterChain.doFilter(httpServletRequest, httpServletResponse);
                return;
            }
            if (JwtUtil.isVerify(token, user)){
                List<SimpleGrantedAuthority> simpleGrantedAuthorities = authorityService.selectByUserId(user);
                UsernamePasswordAuthenticationToken authentication =
                        new UsernamePasswordAuthenticationToken(user, null, simpleGrantedAuthorities);
                authentication.setDetails(new WebAuthenticationDetailsSource().buildDetails(httpServletRequest));
                SecurityContextHolder.getContext().setAuthentication(authentication);
            }
        }
        filterChain.doFilter(httpServletRequest, httpServletResponse);
    }
}
