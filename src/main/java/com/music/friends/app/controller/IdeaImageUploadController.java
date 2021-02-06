package com.music.friends.app.controller;

import com.music.friends.app.exception.CustomException;
import com.music.friends.app.utils.AlibabaOSSUtil;
import com.music.friends.app.utils.ResponseGenerator;
import com.music.friends.app.utils.ResponseResult;
import com.music.friends.app.utils.SpringSecurityUtil;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@RestController
@RequestMapping("ideaImage")
public class IdeaImageUploadController {

    @PostMapping("upload")
    @PreAuthorize("hasAuthority('/ideaImage/upload')")
    public ResponseResult upload(MultipartFile file){
        String fileName = file.getOriginalFilename();
        if (fileName == null){
            return ResponseGenerator.getFailResult();
        }
        String suffix = fileName.substring(fileName.lastIndexOf("."));
        try {
            String url = AlibabaOSSUtil.streamUpload(file.getInputStream(), SpringSecurityUtil.getUserName(), "image", suffix);
            return ResponseGenerator.getSuccessResult("url", url);
        } catch (CustomException | IOException e) {
            e.printStackTrace();
            return ResponseGenerator.getFailResult(e.getMessage());
        }
    }

}
