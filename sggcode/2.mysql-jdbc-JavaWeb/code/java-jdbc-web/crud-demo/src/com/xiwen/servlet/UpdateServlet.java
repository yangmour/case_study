package com.xiwen.servlet;

import com.xiwen.service.SoldierService;
import com.xiwen.service.impl.SoldierServiceImpl;
import com.xiwen.utils.ViewBaseServlet;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * Description:
 *
 * @author: yf
 * @Create: 2023/03/21 -19:20
 * @Version: 1.0
 */
@WebServlet(value = "/updateServlet")
public class UpdateServlet extends ViewBaseServlet {
    private SoldierService soldierService = new SoldierServiceImpl();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        doPost(request, response);
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {

        String id = request.getParameter("id");
        String name = request.getParameter("name");
        String weapon = request.getParameter("weapon");
        String update = request.getParameter("update");
        if (update == null) {
            boolean f = soldierService.saveSoldier(name, weapon);
            if (f) {
                response.sendRedirect(request.getContextPath() + "/index.html");
            } else {
                request.setAttribute("mgs", "保存失败!");
                processTemplate("save", request, response);
            }
        } else if ("update".equals(update)) {
            request.setAttribute("t_id", id);
            request.setAttribute("t_name", name);
            request.setAttribute("t_weapon", weapon);
            processTemplate("update", request, response);
        }


    }
}