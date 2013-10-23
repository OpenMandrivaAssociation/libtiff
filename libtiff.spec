%define major	5
%define libname	%mklibname tiff %{major}
%define libxx	%mklibname tiffxx %{major}
%define devname	%mklibname tiff -d

Summary:	A library of functions for manipulating TIFF format image files
Name:		libtiff
Version:	4.0.3
Release:	5
License:	BSD-like
Group:		System/Libraries
Url:		http://www.remotesensing.org/libtiff/
Source0:	ftp://ftp.remotesensing.org/pub/libtiff/tiff-%{version}.tar.gz
Patch1:		tiff-3.9.1-no_contrib.diff
BuildRequires:	libtool
BuildRequires:	jbig-devel
BuildRequires:	jpeg-devel
BuildRequires:	pkgconfig(glut)
BuildRequires:	pkgconfig(zlib)

%description
The libtiff package contains a library of functions for manipulating TIFF
(Tagged Image File Format) image format files. TIFF is a widely used file
format for bitmapped images. TIFF files usually end in the .tif extension
and they are often quite large.

%package	progs
Summary:	Binaries needed to manipulate TIFF format image files
Group:		Graphics

%description	progs
This package provides binaries needed to manipulate TIFF format image files.

%package -n	%{libname}
Summary:	A library of functions for manipulating TIFF format image files
Group:		System/Libraries

%description -n	%{libname}
The libtiff package contains a library of functions for manipulating TIFF
(Tagged Image File Format) image format files. TIFF is a widely used file
format for bitmapped images. TIFF files usually end in the .tif extension
and they are often quite large.

%package -n	%{libxx}
Summary:	A library of functions for manipulating TIFF format image files
Group:		System/Libraries
Conflicts:	%{_lib}tiff5 < 4.0.3-2

%description -n	%{libxx}
This package contains a shared library for %{name}.

%package -n	%{devname}
Summary:	Development tools for programs which will use the libtiff library
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Requires:	%{libxx} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	tiff-devel = %{version}-%{release}

%description -n	%{devname}
This package contains the header files and .so libraries for developing
programs which will manipulate TIFF format image files using the libtiff
library.

%prep
%setup -qn tiff-%{version}
%apply_patches

# cleanup
for i in `find . -type d -name CVS` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

# Use build system's libtool.m4, not the one in the package.
rm -f libtool.m4
autoreconf -fi

%build
export LDFLAGS="%{ldflags}"
export CFLAGS="%{optflags} -fno-strict-aliasing"
export CXXFLAGS="%{optflags}"

%configure2_5x \
	--disable-static \
	--enable-ld-version-script

%make

#temporary disabled due upstream fix
#%check
# 
%install
mkdir -p %{buildroot}/{%{_bindir},%{_datadir}}
rm -rf installed_docs
%makeinstall LIBTIFF_DOCDIR=`pwd`/installed_docs

install -m0644 libtiff/tiffiop.h %{buildroot}%{_includedir}/
install -m0644 libtiff/tif_dir.h %{buildroot}%{_includedir}/

# multiarch policy
%multiarch_includes %{buildroot}%{_includedir}/tiffconf.h

# cleanup
%files progs
%{_bindir}/*
%{_mandir}/man1/*

%files -n %{libname}
%{_libdir}/libtiff.so.%{major}*

%files -n %{libxx}
%{_libdir}/libtiffxx.so.%{major}*

%files -n %{devname}
%doc installed_docs/*
%{_includedir}/*.h*
%{multiarch_includedir}/tiffconf.h
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc
%{_mandir}/man3/*

