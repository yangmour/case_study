package com.xiwen; /**
 * Description:
 *
 * @author: yf
 * @Create: 2023/03/24 -15:32
 * @Version: 1.0
 */

import com.xiwen.base.ViewBaseServlet;

import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.*;
import java.io.IOException;

@WebServlet("/index.html")
public class IndexServlet extends ViewBaseServlet {
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        doPost(request, response);
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        HttpSession session = request.getSession();
        //如果是新创建的session就让他失效并跳到登陆页面
        if (session.isNew()) {
            session.invalidate();
        }

        //没有失效将跳到首页
        processTemplate("index", request, response);
    }
}
