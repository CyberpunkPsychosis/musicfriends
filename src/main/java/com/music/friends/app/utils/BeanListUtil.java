package com.music.friends.app.utils;

import cn.hutool.core.bean.BeanUtil;
import com.music.friends.app.exception.CustomException;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

/**
 * 对象列表转换工具类
 */
public class BeanListUtil {

    public static <E,T> List<T> toBeanList(Collection<E> objects, Class<T> clazz) throws CustomException {
        if (objects.size() == 0){
            return new ArrayList<>();
        } else {
            List<T> list = new ArrayList<>();
            for (Object object : objects) {
                list.add(BeanUtil.toBean(object, clazz));
            }
            return list;
        }
    }

}
