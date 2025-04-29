@ExtendWith(MockitoExtension.class)
class ProxyAssignmentServiceImplTest {

    @InjectMocks
    private ProxyAssignmentServicelmpl proxyAssignmentService;

    @Mock
    private UsrProxyDao usrProxyDao;

    @Mock
    private LDAPService ldapService;

    @Mock
    private UserRoleReaderService userRoleReaderService;

    @Mock
    private AppFlwTypService aftService;

    @Mock
    private EntityManager entityManager;

    @Test
    void testActivateProxy_whenProxyAlreadyExists() {
        // Mock static UserDetails
        try (MockedStatic<UserDetails> utilities = mockStatic(UserDetails.class)) {
            LDAPUserInfoDto proxyUser = new LDAPUserInfoDto();
            proxyUser.setEmpld("proxyEmpId");
            proxyUser.setAdEntId("proxyAdEntId");

            LDAPUserInfoDto currentUser = new LDAPUserInfoDto();
            currentUser.setEmpld("currentEmpId");
            currentUser.setAdEntId("currentAdEntId");

            utilities.when(() -> UserDetails.getUserByEmpld("proxy123")).thenReturn(proxyUser);
            utilities.when(() -> UserDetails.getUserByEmpld("current456")).thenReturn(currentUser);

            // Mock inside proxyExists
            CriteriaBuilder cb = mock(CriteriaBuilder.class);
            CriteriaQuery<UsrProxy> cq = mock(CriteriaQuery.class);
            Root<UsrProxy> root = mock(Root.class);
            TypedQuery<UsrProxy> query = mock(TypedQuery.class);

            when(entityManager.getCriteriaBuilder()).thenReturn(cb);
            when(cb.createQuery(UsrProxy.class)).thenReturn(cq);
            when(cq.from(UsrProxy.class)).thenReturn(root);
            when(entityManager.createQuery(cq)).thenReturn(query);

            List<UsrProxy> proxyList = new ArrayList<>();
            proxyList.add(new UsrProxy()); // proxy exists
            when(query.getResultList()).thenReturn(proxyList);

            // Act
            ProxyAssignmentResult result = proxyAssignmentService.activateProxy("proxy123", 1L, "current456");

            // Assert
            assertEquals(Constants.FAIL, result.getResult());
            assertEquals("This proxy already exists for this user.", result.getMessage());
        }
    }
}




package com.wellsfargo.mortgage.servicing.slr.service.impl;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

import com.wellsfargo.mortgage.servicing.sir.domain.dto.LDAPUserInfoDto;
import com.wellsfargo.mortgage.servicing.slr.domain.entities.UsrProxy;
import com.wellsfargo.mortgage.servicing.str.domain.repositories.UsrProxyDao;
import com.wellsfargo.mortgage.servicing.sir.utility.Constants;
import com.wellsfargo.mortgage.servicing.slr.utility.UserDetails;
import jakarta.persistence.EntityManager;
import jakarta.persistence.criteria.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.*;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.ZonedDateTime;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class ProxyAssignmentServicelmplTest {

    @InjectMocks
    private ProxyAssignmentServicelmpl proxyAssignmentService;

    @Mock
    private UsrProxyDao usrProxyDao;

    @Mock
    private EntityManager entityManager;

    @Mock
    private CriteriaBuilder criteriaBuilder;

    @Mock
    private CriteriaQuery<UsrProxy> criteriaQuery;

    @Mock
    private Root<UsrProxy> root;

    @BeforeEach
    void setup() {
        proxyAssignmentService = new ProxyAssignmentServicelmpl();
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void testDeactivateProxy_usrProxyFound_updatesSuccessfully() {
        String proxyEmpld = "proxy123";
        Long ida = 1L;
        String empld = "empld123";

        // Mock static UserDetails.getUserByEmpld
        LDAPUserInfoDto ldapUserInfoDto = new LDAPUserInfoDto();
        ldapUserInfoDto.setEmpld("proxy123");

        try (MockedStatic<UserDetails> mocked = Mockito.mockStatic(UserDetails.class)) {
            mocked.when(() -> UserDetails.getUserByEmpld(proxyEmpld)).thenReturn(ldapUserInfoDto);

            when(entityManager.getCriteriaBuilder()).thenReturn(criteriaBuilder);
            when(criteriaBuilder.createQuery(UsrProxy.class)).thenReturn(criteriaQuery);
            when(criteriaQuery.from(UsrProxy.class)).thenReturn(root);
            when(entityManager.createQuery(any(CriteriaQuery.class))).thenReturn(mock(javax.persistence.TypedQuery.class));

            UsrProxy usrProxy = new UsrProxy();
            when(entityManager.createQuery(any(CriteriaQuery.class)).getResultList()).thenReturn(List.of(usrProxy));

            ProxyAssignmentResult result = proxyAssignmentService.deactivateProxy(proxyEmpld, ida, empld);

            verify(usrProxyDao, times(1)).save(any(UsrProxy.class));
            assertEquals(Constants.OK, result.getMessage());
            assertEquals(Constants.OK, result.getResult());
        }
    }

    @Test
    void testDeactivateProxy_noUsrProxyFound_doesNothing() {
        String proxyEmpld = "proxy123";
        Long ida = 1L;
        String empld = "empld123";

        LDAPUserInfoDto ldapUserInfoDto = new LDAPUserInfoDto();
        ldapUserInfoDto.setEmpld("proxy123");

        try (MockedStatic<UserDetails> mocked = Mockito.mockStatic(UserDetails.class)) {
            mocked.when(() -> UserDetails.getUserByEmpld(proxyEmpld)).thenReturn(ldapUserInfoDto);

            when(entityManager.getCriteriaBuilder()).thenReturn(criteriaBuilder);
            when(criteriaBuilder.createQuery(UsrProxy.class)).thenReturn(criteriaQuery);
            when(criteriaQuery.from(UsrProxy.class)).thenReturn(root);
            when(entityManager.createQuery(any(CriteriaQuery.class))).thenReturn(mock(javax.persistence.TypedQuery.class));

            when(entityManager.createQuery(any(CriteriaQuery.class)).getResultList()).thenReturn(Collections.emptyList());

            ProxyAssignmentResult result = proxyAssignmentService.deactivateProxy(proxyEmpld, ida, empld);

            verify(usrProxyDao, never()).save(any(UsrProxy.class));
            assertNull(result.getMessage());
            assertNull(result.getResult());
        }
    }

    @Test
    void testDeactivateProxy_nullProxyEmpld_treatedAsEmptyString() {
        String proxyEmpld = null;
        Long ida = 1L;
        String empld = "empld123";

        LDAPUserInfoDto ldapUserInfoDto = new LDAPUserInfoDto();
        ldapUserInfoDto.setEmpld("");

        try (MockedStatic<UserDetails> mocked = Mockito.mockStatic(UserDetails.class)) {
            mocked.when(() -> UserDetails.getUserByEmpld("")).thenReturn(ldapUserInfoDto);

            when(entityManager.getCriteriaBuilder()).thenReturn(criteriaBuilder);
            when(criteriaBuilder.createQuery(UsrProxy.class)).thenReturn(criteriaQuery);
            when(criteriaQuery.from(UsrProxy.class)).thenReturn(root);
            when(entityManager.createQuery(any(CriteriaQuery.class))).thenReturn(mock(javax.persistence.TypedQuery.class));

            when(entityManager.createQuery(any(CriteriaQuery.class)).getResultList()).thenReturn(Collections.emptyList());

            ProxyAssignmentResult result = proxyAssignmentService.deactivateProxy(proxyEmpld, ida, empld);

            assertNull(result.getMessage());
            assertNull(result.getResult());
        }
    }
}@Test
void testDeactivateProxy_Success() {
    // Mock user returned from UserDetails (or LDAPService, depending on your design)
    LDAPUserInfoDto currentUser = new LDAPUserInfoDto();
    currentUser.setEmplId("currentEmp123");
    currentUser.setAdEntId("adCurrent");

    // Simulate getting user details
    when(ldapService.getUserByEmpld("proxyEmp123")).thenReturn(currentUser);

    // Mock CriteriaBuilder and other JPA criteria API components
    CriteriaBuilder cb = mock(CriteriaBuilder.class);
    CriteriaQuery<UsrProxy> cq = mock(CriteriaQuery.class);
    Root<UsrProxy> root = mock(Root.class);

    when(entityManager.getCriteriaBuilder()).thenReturn(cb);
    when(cb.createQuery(UsrProxy.class)).thenReturn(cq);
    when(cq.from(UsrProxy.class)).thenReturn(root);

    // Mock TypedQuery result
    javax.persistence.TypedQuery<UsrProxy> typedQuery = mock(javax.persistence.TypedQuery.class);
    when(entityManager.createQuery(any(CriteriaQuery.class))).thenReturn(typedQuery);

    UsrProxy usrProxy = new UsrProxy();
    usrProxy.setEmpld("adCurrent");
    usrProxy.setProxyEmpld("proxyEmp123");
    usrProxy.setActiveDate(ZonedDateTime.now());
    usrProxy.setInactiveDate(null); // initially active

    when(typedQuery.getResultList()).thenReturn(Collections.singletonList(usrProxy));

    // Execute
    ProxyAssignmentResult result = proxyAssignmentService.deactivateProxy("proxyEmp123", 1L, "currentEmp123");

    // Verify
    assertNotNull(result);
    assertEquals("OK", result.getMessage());
    assertEquals("OK", result.getResult());
    assertNotNull(usrProxy.getInactiveDate()); // should be set now
    verify(usrProxyDao).save(usrProxy);
}
