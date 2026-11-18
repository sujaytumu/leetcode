package com.sujaytumu.leetcode.auth;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletRequestWrapper;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Enumeration;
import java.util.List;
import com.sujaytumu.leetcode.common.Headers;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

/**
 * Makes accounts work with every existing endpoint without touching them: when a valid {@code Authorization:
 * Bearer} token is present, {@code X-Client-Id} is overwritten with the account's id, so a logged-in user cannot
 * act as anyone else. Rejection (bad token, or an account's id used without logging in) is done by
 * {@link AuthInterceptor} so the 401 goes through the normal error handler and CORS headers.
 */
@Component
public class AuthFilter extends OncePerRequestFilter {

    static final String VERIFIED = AuthFilter.class.getName() + ".verified";
    static final String BAD_TOKEN = AuthFilter.class.getName() + ".badToken";

    private final AuthService auth;

    public AuthFilter(AuthService auth) {
        this.auth = auth;
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        return !request.getRequestURI().startsWith("/api/");
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String authorization = request.getHeader(HttpHeaders.AUTHORIZATION);
        if (authorization == null || authorization.isBlank()) {
            chain.doFilter(request, response);
            return;
        }
        var account = auth.accountFor(authorization);
        if (account.isEmpty()) {
            request.setAttribute(BAD_TOKEN, Boolean.TRUE);
            chain.doFilter(request, response);
            return;
        }
        request.setAttribute(VERIFIED, Boolean.TRUE);
        chain.doFilter(new ClientIdOverride(request, account.get().getClientId().toString()), response);
    }

    private static final class ClientIdOverride extends HttpServletRequestWrapper {
        private final String clientId;

        ClientIdOverride(HttpServletRequest request, String clientId) {
            super(request);
            this.clientId = clientId;
        }

        @Override
        public String getHeader(String name) {
            return Headers.CLIENT_ID.equalsIgnoreCase(name) ? clientId : super.getHeader(name);
        }

        @Override
        public Enumeration<String> getHeaders(String name) {
            return Headers.CLIENT_ID.equalsIgnoreCase(name)
                    ? Collections.enumeration(List.of(clientId))
                    : super.getHeaders(name);
        }

        @Override
        public Enumeration<String> getHeaderNames() {
            List<String> names = new ArrayList<>(Collections.list(super.getHeaderNames()));
            if (names.stream().noneMatch(Headers.CLIENT_ID::equalsIgnoreCase)) {
                names.add(Headers.CLIENT_ID);
            }
            return Collections.enumeration(names);
        }
    }
}
