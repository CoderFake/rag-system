import React, { ReactNode, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  AppBar,
  Box,
  CssBaseline,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Menu,
  MenuItem,
  Button,
  useMediaQuery,
  useTheme,
  Badge,
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
} from '@mui/icons-material';
import { useAuth, useLanguage, useTheme as useAppTheme } from '../../contexts';
import { Language } from '../../types';

const getDrawerWidth = (isSmallScreen: boolean) => isSmallScreen ? 240 : 260;

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const theme = useTheme();
  const { isAuthenticated, user, logout } = useAuth();
  const { language, changeLanguage } = useLanguage();
  const { theme: appTheme, toggleTheme } = useAppTheme();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [langAnchorEl, setLangAnchorEl] = useState<null | HTMLElement>(null);

  // Responsive breakpoints
  const isXsScreen = useMediaQuery(theme.breakpoints.down('sm'));
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'));
  const drawerWidth = getDrawerWidth(isSmallScreen);

  const isAdmin = user?.role === 'admin';

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
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
    if (isSmallScreen) {
      setMobileOpen(false); 
    }
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
    {
      text: t('app.documents'),
      icon: <DocumentIcon />,
      path: '/admin/documents',
      onClick: () => handleNavClick('/admin/documents'),
      requireAdmin: true,
    },
    {
      text: t('app.settings'),
      icon: <SettingsIcon />,
      path: '/admin/settings',
      onClick: () => handleNavClick('/admin/settings'),
      requireAdmin: true,
    },
  ];

  const drawer = (
    <div>
      <Toolbar sx={{ 
        px: isSmallScreen ? 1 : 2, 
        height: { xs: 56, sm: 64 }, 
        display: 'flex',
        alignItems: 'center' 
      }}>
        <Typography 
          variant={isSmallScreen ? "subtitle1" : "h6"} 
          noWrap 
          component="div"
          sx={{ 
            fontWeight: 'bold',
            fontSize: isSmallScreen ? '1rem' : '1.25rem' 
          }}
        >
          {t('app.title')}
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => {
          if (
            (item.requireAuth && !isAuthenticated) ||
            (item.requireAdmin && !isAdmin)
          ) {
            return null;
          }
          return (
            <ListItem key={item.text} disablePadding>
              <ListItemButton 
                onClick={item.onClick}
                sx={{ 
                  py: isSmallScreen ? 1 : 1.5,
                  px: isSmallScreen ? 2 : 3
                }}
              >
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex', height: '100vh', width: '100%', overflow: 'hidden' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          boxShadow: 1,
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2, display: { sm: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
            <Typography 
              variant={isXsScreen ? "subtitle1" : "h6"} 
              noWrap 
              component="div" 
              sx={{ 
                flexGrow: 1, 
                display: { xs: isXsScreen ? 'none' : 'block', sm: 'block' } 
              }}
            >
              {t('app.title')}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton 
              color="inherit" 
              onClick={toggleTheme}
              size={isXsScreen ? "small" : "medium"}
              sx={{ ml: isXsScreen ? 0.5 : 1 }}
            >
              {appTheme === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>

            <IconButton 
              color="inherit" 
              onClick={handleLangMenu}
              size={isXsScreen ? "small" : "medium"}
              sx={{ ml: isXsScreen ? 0.5 : 1 }}
            >
              <Badge 
                color="secondary" 
                variant="dot" 
                invisible={language === 'en'}
              >
                <TranslateIcon />
              </Badge>
            </IconButton>
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

            {isAuthenticated ? (
              <div>
                <IconButton
                  size={isXsScreen ? "small" : "medium"}
                  aria-label="account of current user"
                  aria-controls="menu-appbar"
                  aria-haspopup="true"
                  onClick={handleMenu}
                  color="inherit"
                  sx={{ ml: isXsScreen ? 0.5 : 1 }}
                >
                  <AccountCircle />
                </IconButton>
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
                  <MenuItem disabled dense={isXsScreen}>
                    {user?.name || user?.username || t('auth.anonymous')}
                  </MenuItem>
                  <Divider />
                  <MenuItem onClick={handleLogout} dense={isXsScreen}>
                    <ListItemIcon>
                      <LogoutIcon fontSize={isXsScreen ? "small" : "medium"} />
                    </ListItemIcon>
                    {t('app.logout')}
                  </MenuItem>
                </Menu>
              </div>
            ) : (
              <Button
                color="inherit"
                size={isXsScreen ? "small" : "medium"}
                startIcon={isXsScreen ? undefined : <LoginIcon />}
                onClick={() => navigate('/login')}
                sx={{ ml: isXsScreen ? 0.5 : 1 }}
              >
                {isXsScreen ? <LoginIcon /> : t('app.login')}
              </Button>
            )}
          </Box>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="mailbox folders"
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          height: '100vh',
          overflow: 'auto',
          p: { xs: 1, sm: 2, md: 3 }
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};

export default Layout;