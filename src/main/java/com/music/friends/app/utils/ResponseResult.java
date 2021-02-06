package com.music.friends.app.utils;

import lombok.Data;

import java.util.HashMap;
import java.util.Map;

@Data
public class ResponseResult {

    private Integer code;

    private String message = "success";

    private Map<String, Object> data = new HashMap<>();

    public ResponseResult setCode(Integer code){
        this.code = code;
        return this;
    }

    public ResponseResult setMessage(String message){
        this.message = message;
        return this;
    }

    public ResponseResult setData(String key, Object data){
        this.data.put(key, data);
        return this;
    }
}
