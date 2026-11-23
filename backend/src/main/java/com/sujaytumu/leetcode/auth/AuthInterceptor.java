package com.sujaytumu.leetcode.auth;

import com.sujaytumu.leetcode.common.ApiExceptions.UnauthorizedException;
import com.sujaytumu.leetcode.common.Headers;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.util.UUID;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

/**
 * Rejects (401) requests with an invalid or expired token, and requests that use an account's client id
 * without a valid token. That second rule is what makes an account private: the id alone no longer grants access.
 */
@Component
public class AuthInterceptor implements HandlerInterceptor {

    private final BoundClients bound;

    public AuthInterceptor(BoundClients bound) {
        this.bound = bound;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        if (request.getAttribute(AuthFilter.BAD_TOKEN) != null) {
            throw new UnauthorizedException("Your session expired. Please log in again.");
        }
        if (request.getAttribute(AuthFilter.VERIFIED) != null) {
            return true;
        }
        String raw = request.getHeader(Headers.CLIENT_ID);
        if (raw == null) {
            return true;
        }
        try {
            if (bound.isBound(UUID.fromString(raw.trim()))) {
                throw new UnauthorizedException("This id belongs to an account. Please log in.");
            }
        } catch (IllegalArgumentException ignored) {
            // malformed ids are rejected by the controllers' own header parsing
        }
        return true;
    }
}
