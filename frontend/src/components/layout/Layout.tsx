import React, { ReactNode, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './Layout.css';
import {
  Box,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Menu,
  MenuItem,
  Button,
  useTheme,
  useMediaQuery,
  Badge,
  Avatar,
  Collapse,
  Switch,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Chat as ChatIcon,
  History as HistoryIcon,
  Description as DocumentIcon,
  Settings as SettingsIcon,
  Translate as TranslateIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  AccountCircle,
  Login as LoginIcon,
  Logout as LogoutIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  ExpandLess,
  ExpandMore,
  Settings,
} from '@mui/icons-material';
import { useAuth, useLanguage, useTheme as useAppTheme } from '../../contexts';
import { Language } from '../../types';

interface LayoutProps {
  children: ReactNode;
}

const drawerWidth = 260;
const collapsedDrawerWidth = 75;

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const theme = useTheme();
  const { isAuthenticated, user, logout } = useAuth();
  const { language, changeLanguage } = useLanguage();
  const { theme: appTheme, toggleTheme } = useAppTheme();
  
  const isMdUp = useMediaQuery(theme.breakpoints.up('md'));
  const [open, setOpen] = useState(isMdUp); 
  const [mobileOpen, setMobileOpen] = useState(false);
  
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [langAnchorEl, setLangAnchorEl] = useState<null | HTMLElement>(null);
  const [adminMenuOpen, setAdminMenuOpen] = useState(false);

  const isXsScreen = useMediaQuery(theme.breakpoints.down('sm'));
  const isMdScreen = useMediaQuery(theme.breakpoints.down('md')); 

  const isAdmin = user?.role === 'admin';

  useEffect(() => {
    setOpen(isMdUp);
  }, [isMdUp]);

  const handleDrawerToggle = () => {
    if (isMdScreen) {
      setMobileOpen(!mobileOpen);
    } else {
      setOpen(!open);
    }
  };

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLangMenu = (event: React.MouseEvent<HTMLElement>) => {
    setLangAnchorEl(event.currentTarget);
  };

  const handleLangClose = () => {
    setLangAnchorEl(null);
  };

  const handleLanguageChange = (lang: Language) => {
    changeLanguage(lang);
    handleLangClose();
  };

  const handleLogout = () => {
    logout();
    handleClose();
    navigate('/');
  };

  const handleNavClick = (path: string) => {
    navigate(path);
    if (isMdScreen) {
      setMobileOpen(false); 
    }
  };

  const handleAdminMenuToggle = () => {
    setAdminMenuOpen(!adminMenuOpen);
  };

  const menuItems = [
    {
      text: t('app.chat'),
      icon: <ChatIcon />,
      path: '/',
      onClick: () => handleNavClick('/'),
    },
    {
      text: t('app.history'),
      icon: <HistoryIcon />,
      path: '/history',
      onClick: () => handleNavClick('/history'),
      requireAuth: true,
    },
  ];

  const adminMenuItems = [
    {
      text: t('app.documents'),
      icon: <DocumentIcon />,
      path: '/admin/documents',
      onClick: () => handleNavClick('/admin/documents'),
    },
    {
      text: t('app.settings'),
      icon: <SettingsIcon />,
      path: '/admin/settings',
      onClick: () => handleNavClick('/admin/settings'),
    },
  ];

  const drawerContent = (
    <Box sx={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      background: theme.palette.mode === 'dark' 
        ? 'linear-gradient(180deg, rgba(26,32,44,1) 0%, rgba(17,24,39,1) 100%)' 
        : 'linear-gradient(180deg, rgba(255,255,255,1) 0%, rgba(249,250,251,1) 100%)',
    }}>
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        padding: theme.spacing(0, 1), 
        ...theme.mixins.toolbar,
        borderBottom: `1px solid ${theme.palette.divider}`,
      }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          padding: theme.spacing(0, 2),
          minWidth: open ? 180 : 0,
          visibility: open ? 'visible' : 'hidden',
          opacity: open ? 1 : 0, 
          transition: theme.transitions.create(['opacity', 'visibility'], {
             easing: theme.transitions.easing.sharp,
             duration: theme.transitions.duration.enteringScreen,
          }),
        }}>
          <Typography 
            variant={isXsScreen ? "h6" : "h5"} 
            noWrap
            sx={{ 
              fontWeight: 700,
              whiteSpace: 'nowrap',
              background: theme.palette.mode === 'dark' 
                ? 'linear-gradient(45deg, #6b46c1 30%, #3182ce 90%)' 
                : 'linear-gradient(45deg, #4338ca 30%, #3b82f6 90%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            {t('app.title')}
          </Typography>
        </Box>
        {!isMdScreen && ( 
          <IconButton onClick={handleDrawerToggle}>
            {open ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          </IconButton>
        )}
      </Box>
      <Divider />
      <List component="nav" sx={{ flexGrow: 1, overflowY: 'auto', overflowX: 'hidden', pt: 0 }}>
        {menuItems.map((item) => {
          if (item.requireAuth && !isAuthenticated) {
            return null;
          }
          return (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                onClick={item.onClick}
                sx={{
                  minHeight: 48,
                  px: 2.5,
                  my: 0.5,
                  borderRadius: '8px',
                  mx: 1,
                  justifyContent: open ? 'initial' : 'center',
                  '&:hover': {
                    backgroundColor: theme.palette.mode === 'dark' 
                      ? 'rgba(255, 255, 255, 0.1)' 
                      : 'rgba(0, 0, 0, 0.04)',
                  },
                  '&.Mui-selected': {
                    backgroundColor: theme.palette.mode === 'dark' 
                      ? 'rgba(255, 255, 255, 0.15)' 
                      : 'rgba(0, 0, 0, 0.08)',
                  },
                }}
                selected={window.location.pathname === item.path}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: open ? 3 : 'auto',
                    justifyContent: 'center',
                    color: window.location.pathname === item.path 
                      ? theme.palette.primary.main 
                      : theme.palette.text.secondary,
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                {open && (
                  <ListItemText 
                    primary={item.text} 
                    sx={{ 
                      display: 'block',
                      color: window.location.pathname === item.path 
                        ? theme.palette.primary.main 
                        : theme.palette.text.secondary,
                      fontWeight: window.location.pathname === item.path ? 600 : 400,
                    }} 
                  />
                )}
              </ListItemButton>
            </ListItem>
          );
        })}

        {isAdmin && (
          <>
            <ListItem disablePadding>
              <ListItemButton
                onClick={handleAdminMenuToggle}
                sx={{
                  minHeight: 48,
                  px: 2.5,
                  my: 0.5,
                  borderRadius: '8px',
                  mx: 1,
                  justifyContent: open ? 'initial' : 'center',
                  '&:hover': {
                    backgroundColor: theme.palette.mode === 'dark' 
                      ? 'rgba(255, 255, 255, 0.1)' 
                      : 'rgba(0, 0, 0, 0.04)',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: open ? 3 : 'auto',
                    justifyContent: 'center',
                    color: adminMenuOpen
                      ? theme.palette.primary.main
                      : theme.palette.text.secondary,
                  }}
                >
                  <Settings />
                </ListItemIcon>
                {open && (
                  <ListItemText 
                    primary={t('app.admin')} 
                    sx={{ 
                      display: 'block',
                      color: adminMenuOpen
                        ? theme.palette.primary.main
                        : theme.palette.text.secondary,
                      fontWeight: adminMenuOpen ? 600 : 400,
                    }} 
                  />
                )}
                {open && (adminMenuOpen ? <ExpandLess /> : <ExpandMore />)}
              </ListItemButton>
            </ListItem>
            <Collapse in={adminMenuOpen && open} timeout="auto" unmountOnExit>
              <List component="div" disablePadding>
                {adminMenuItems.map((item) => (
                  <ListItem key={item.text} disablePadding>
                    <ListItemButton
                      onClick={item.onClick}
                      sx={{
                        minHeight: 48,
                        px: 2.5,
                        py: 1,
                        pl: open ? 4 : 2.5,
                        ml: open ? 2 : 0,
                        borderRadius: '8px',
                        mx: 1,
                        justifyContent: open ? 'initial' : 'center',
                        '&:hover': {
                          backgroundColor: theme.palette.mode === 'dark' 
                            ? 'rgba(255, 255, 255, 0.1)' 
                            : 'rgba(0, 0, 0, 0.04)',
                        },
                        '&.Mui-selected': {
                          backgroundColor: theme.palette.mode === 'dark' 
                            ? 'rgba(255, 255, 255, 0.15)' 
                            : 'rgba(0, 0, 0, 0.08)',
                        },
                      }}
                      selected={window.location.pathname === item.path}
                    >
                      <ListItemIcon
                        sx={{
                          minWidth: 0,
                          mr: open ? 2 : 'auto',
                          color: window.location.pathname === item.path 
                            ? theme.palette.primary.main 
                            : theme.palette.text.secondary,
                        }}
                      >
                        {item.icon}
                      </ListItemIcon>
                      {open && (
                        <ListItemText 
                          primary={item.text} 
                          sx={{ 
                            display: 'block',
                            color: window.location.pathname === item.path 
                              ? theme.palette.primary.main 
                              : theme.palette.text.secondary,
                            fontWeight: window.location.pathname === item.path ? 600 : 400,
                          }} 
                        />
                      )}
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            </Collapse>
          </>
        )}
      </List>
      <Divider />
      <List>
        <ListItem disablePadding>
          <ListItemButton
            sx={{
              minHeight: 48,
              px: 2.5,
              justifyContent: open ? 'initial' : 'center',
              my: 1,
              borderRadius: '8px',
              mx: 1,
            }}
          >
            <ListItemIcon
              sx={{
                minWidth: 0,
                mr: open ? 3 : 'auto',
                justifyContent: 'center',
              }}
            >
              {appTheme === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
            </ListItemIcon>
            {open && (
              <ListItemText 
                primary={t('app.theme')} 
                sx={{ display: 'block' }} 
              />
            )}
            {open && (
              <Switch
                checked={appTheme === 'dark'}
                onChange={toggleTheme}
                color="primary"
              />
            )}
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton
            sx={{
              minHeight: 48,
              px: 2.5,
              justifyContent: open ? 'initial' : 'center',
              my: 1,
              borderRadius: '8px',
              mx: 1,
            }}
            onClick={handleLangMenu}
          >
            <ListItemIcon
              sx={{
                minWidth: 0,
                mr: open ? 3 : 'auto',
                justifyContent: 'center',
              }}
            >
              <Badge 
                color="secondary" 
                variant="dot" 
                invisible={language === 'en'}
              >
                <TranslateIcon />
              </Badge>
            </ListItemIcon>
            {open && (
              <ListItemText 
                primary={t('app.language')} 
                secondary={language === 'vi' ? 'Tiếng Việt' : 'English'}
                sx={{ 
                  display: 'block',
                  '& .MuiListItemText-secondary': {
                    fontSize: '0.8rem'
                  }
                }} 
              />
            )}
          </ListItemButton>
        </ListItem>
      </List>
      <Menu
        id="language-menu"
        anchorEl={langAnchorEl}
        open={Boolean(langAnchorEl)}
        onClose={handleLangClose}
        transformOrigin={{ 
          vertical: 'top',
          horizontal: 'right',
        }}
        anchorOrigin={{ 
          vertical: 'bottom',
          horizontal: 'right',
        }}
      >
        <MenuItem
          onClick={() => handleLanguageChange('vi')}
          selected={language === 'vi'}
          dense={isXsScreen}
        >
          Tiếng Việt
        </MenuItem>
        <MenuItem
          onClick={() => handleLanguageChange('en')}
          selected={language === 'en'}
          dense={isXsScreen}
        >
          English
        </MenuItem>
      </Menu>
      <Divider />
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: open ? 'initial' : 'center' }}>
        {isAuthenticated ? (
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              width: '100%',
              justifyContent: open ? 'space-between' : 'center',
              px: open ? 1 : 0
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Avatar 
                src=""
                sx={{ 
                  width: 32, 
                  height: 32,
                  mr: open ? 2 : 0,
                  background: theme.palette.primary.main,
                  color: theme.palette.primary.contrastText,
                }}
              >
                {user?.name?.charAt(0) || user?.username?.charAt(0) || 'U'}
              </Avatar>
              {open && ( 
                <Box sx={{ minWidth: 0, maxWidth: 120 }}>
                  <Typography variant="body2" noWrap sx={{ fontWeight: 600 }}>
                    {user?.name || user?.username}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" noWrap>
                    {user?.role === 'admin' ? t('app.admin') : t('app.user')}
                  </Typography>
                </Box>
              )}
            </Box>
            {open && ( 
              <IconButton 
                onClick={handleLogout}
                size="small"
                sx={{
                  ml: 1,
                  color: theme.palette.error.main,
                  '&:hover': {
                    background: theme.palette.error.main + '20',
                  }
                }}
              >
                <LogoutIcon fontSize="small" />
              </IconButton>
            )}
          </Box>
        ) : (
          <Button
            variant="outlined"
            startIcon={<LoginIcon />}
            fullWidth={open} // Full width only when open
            onClick={() => navigate('/login')}
            sx={{
              borderRadius: '20px',
              py: 1,
              textTransform: 'none',
              minWidth: open ? 'auto' : 40, 
              px: open ? 2 : 1,
            }}
          >
            {open ? t('app.login') : ''}
          </Button>
        )}
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      {/* AppBar only for mobile (xs screens) */}
      <AppBar
        position="fixed"
        sx={{
          display: { xs: 'block', sm: 'none' },
          boxShadow: 'none',
          backdropFilter: 'blur(10px)',
          background: theme.palette.mode === 'dark'
            ? 'rgba(17, 24, 39, 0.8)'
            : 'rgba(255, 255, 255, 0.8)',
          borderBottom: `1px solid ${theme.palette.divider}`,
        }}
      >
        <Toolbar>
          <IconButton
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ 
              mr: 2,
              color: theme.palette.mode === 'dark' ? 'white' : 'rgba(0, 0, 0, 0.87)'
            }}
          >
            <MenuIcon />
          </IconButton>
          <Typography 
            variant="h6" 
            noWrap 
            component="div"
            sx={{ 
              flexGrow: 1,
              fontWeight: 700,
              background: theme.palette.mode === 'dark' 
                ? 'linear-gradient(45deg, #6b46c1 30%, #3182ce 90%)' 
                : 'linear-gradient(45deg, #4338ca 30%, #3b82f6 90%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            {t('app.title')}
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {/* FIX BUG 4: Fixed color issue with theme toggle button */}
            <IconButton 
              onClick={toggleTheme}
              size="small"
              sx={{ 
                ml: 1,
                color: theme.palette.mode === 'dark' ? 'white' : 'rgba(0, 0, 0, 0.87)'
              }}
            >
              {appTheme === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>

            {/* FIX BUG 4: Fixed color issue with language button */}
            <IconButton 
              onClick={handleLangMenu}
              size="small"
              sx={{ 
                ml: 1,
                color: theme.palette.mode === 'dark' ? 'white' : 'rgba(0, 0, 0, 0.87)'
              }}
            >
              <Badge 
                color="secondary" 
                variant="dot" 
                invisible={language === 'en'}
              >
                <TranslateIcon />
              </Badge>
            </IconButton>

            {isAuthenticated ? (
              <IconButton
                size="small"
                aria-label="account of current user"
                aria-controls="menu-appbar"
                aria-haspopup="true"
                onClick={handleMenu}
                sx={{ 
                  ml: 1,
                  color: theme.palette.mode === 'dark' ? 'white' : 'rgba(0, 0, 0, 0.87)'
                }}
              >
                <AccountCircle />
              </IconButton>
            ) : (
              <Button
                color="inherit"
                size="small"
                startIcon={<LoginIcon />}
                onClick={() => navigate('/login')}
                sx={{ 
                  ml: 1,
                  color: theme.palette.mode === 'dark' ? 'white' : 'rgba(0, 0, 0, 0.87)'
                }}
              >
                {t('app.login')}
              </Button>
            )}
          </Box>
        </Toolbar>
      </AppBar>

      {/* Menu for user options */}
      <Menu
        id="menu-appbar"
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        keepMounted
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
        <MenuItem onClick={handleClose}>
          {t('app.profile')}
        </MenuItem>
        <MenuItem onClick={handleLogout}>
          {t('app.logout')}
        </MenuItem>
      </Menu>

      {/* Drawer Navigation */}
      <Drawer
        variant={isMdScreen ? "temporary" : "permanent"}
        open={isMdScreen ? mobileOpen : open}
        onClose={isMdScreen ? handleDrawerToggle : undefined}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          width: { md: open ? drawerWidth : collapsedDrawerWidth },
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: isMdScreen ? drawerWidth : (open ? drawerWidth : collapsedDrawerWidth),
            boxSizing: 'border-box',
            overflowX: 'hidden',
            border: 'none',
            boxShadow: isMdScreen ? 3 : 'none',
            transition: theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
          },
        }}
      >
        {drawerContent}
      </Drawer>
      
      {/* Toggle button for collapsed sidebar on medium+ screens */}
      {!isMdScreen && !open && (
        <Box
          sx={{
            position: 'fixed',
            top: '50%',
            left: 0,
            zIndex: 1200,
            transform: 'translateY(-50%)',
            transition: theme.transitions.create('all', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
          }}
        >
          <IconButton
            onClick={handleDrawerToggle}
            aria-label="open drawer"
            sx={{
              backgroundColor: theme.palette.primary.main,
              color: theme.palette.primary.contrastText,
              borderRadius: '0 4px 4px 0',
              '&:hover': {
                backgroundColor: theme.palette.primary.dark,
              },
            }}
          >
            <ChevronRightIcon />
          </IconButton>
        </Box>
      )}

      {/* Main Content Area - Simplified */}
      <Box
        component="main"
        className="main-content"
        sx={{
          flexGrow: 1,
          width: { xs: '100%', md: `calc(100% - ${open ? drawerWidth : collapsedDrawerWidth}px)` },
          height: '100vh',
          overflow: 'auto',
          p: { xs: 1, sm: 2, md: 3 },
          pt: { xs: `calc(${theme.mixins.toolbar.minHeight}px + ${theme.spacing(1)})`, sm: 2, md: 3 },
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
          background: theme.palette.mode === 'dark'
            ? 'radial-gradient(circle at 50% 50%, rgba(29, 32, 43, 1) 0%, rgba(15, 23, 42, 1) 100%)'
            : 'radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 1) 0%, rgba(247, 250, 252, 1) 100%)',
        }}
      >
        {/* No need for Toolbar spacer here, padding handles it */}
        {children}
      </Box>
    </Box>
  );
};

export default Layout;