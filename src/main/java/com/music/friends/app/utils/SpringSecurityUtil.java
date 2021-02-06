package com.music.friends.app.utils;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.User;

/**
 * SpringSecurity工具类
 */
public class SpringSecurityUtil {

    public static Authentication getAuthentication(){
        SecurityContext context = SecurityContextHolder.getContext();
        return context.getAuthentication();
    }

    /**
     * 获取当前用户
     * @return String
     */
    public static String getUserName(){
        Object object = getAuthentication().getPrincipal();
        if (object instanceof User){
            User user = (User)getAuthentication().getPrincipal();
            return user.getUsername();
        }
        if (object instanceof com.music.friends.app.pojo.User){
            com.music.friends.app.pojo.User user = (com.music.friends.app.pojo.User)getAuthentication().getPrincipal();
            return user.getAccount();
        }
        return null;
    }
}
